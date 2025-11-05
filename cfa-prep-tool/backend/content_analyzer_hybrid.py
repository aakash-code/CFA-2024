"""Hybrid content analyzer using intelligent routing between Ollama, OpenRouter, and Claude API."""
import os
import json
import anthropic
import httpx
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()


class HybridContentAnalyzer:
    """Analyze CFA content using hybrid routing for cost optimization."""

    def __init__(self, api_key: str = None):
        self.anthropic_api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
        self.use_hybrid = os.getenv("USE_HYBRID_ROUTING", "true").lower() == "true"
        self.routing_preference = os.getenv("ROUTING_PREFERENCE", "cost_optimized")

        # Initialize clients
        self.claude_client = anthropic.Anthropic(api_key=self.anthropic_api_key) if self.anthropic_api_key else None

        # Cost tracking
        self.total_cost = 0.0
        self.request_count = {
            "ollama": 0,
            "openrouter": 0,
            "anthropic": 0
        }

    def _analyze_complexity(self, content: str, task_type: str) -> str:
        """Determine complexity level: simple, medium, or complex."""
        content_lower = content.lower()

        # High complexity indicators
        high_keywords = [
            "ethics", "case study", "vignette", "scenario", "integration",
            "comprehensive", "analyze multiple", "synthesize"
        ]

        # Medium complexity indicators
        medium_keywords = [
            "calculate", "apply", "analyze", "compare", "evaluate",
            "demonstrate", "derive", "interpret"
        ]

        # Check for high complexity
        if any(keyword in content_lower for keyword in high_keywords):
            return "complex"

        # Check for medium complexity
        if any(keyword in content_lower for keyword in medium_keywords):
            return "medium"

        # Check content length
        if len(content) > 3000:
            return "medium"

        # Default to simple
        return "simple"

    def _select_provider(self, complexity: str, task_type: str) -> tuple[str, str]:
        """
        Select the best provider and model based on complexity and routing preference.
        Returns: (provider, model)
        """
        if not self.use_hybrid:
            return ("anthropic", "claude-3-5-sonnet-20241022")

        # Cost-optimized routing (default)
        if self.routing_preference == "cost_optimized":
            if complexity == "simple":
                return ("ollama", "qwen2.5-coder:7b")
            elif complexity == "medium":
                if task_type == "flashcards":
                    return ("ollama", "deepseek-coder:33b")
                else:
                    return ("openrouter", "qwen/qwen-2.5-coder-32b-instruct:free")
            else:  # complex
                return ("anthropic", "claude-3-5-sonnet-20241022")

        # Balanced routing
        elif self.routing_preference == "balanced":
            if complexity == "simple":
                return ("ollama", "deepseek-coder:33b")
            elif complexity == "medium":
                return ("openrouter", "qwen/qwen-2.5-coder-32b-instruct:free")
            else:
                return ("anthropic", "claude-3-5-sonnet-20241022")

        # Quality-first routing (use Claude more often)
        else:
            if complexity == "simple":
                return ("ollama", "deepseek-coder:33b")
            else:
                return ("anthropic", "claude-3-5-sonnet-20241022")

    def _call_ollama(self, prompt: str, model: str, max_tokens: int = 4000) -> str:
        """Call local Ollama model."""
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{self.ollama_base_url}/chat/completions",
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": max_tokens,
                        "temperature": 0.7
                    }
                )
                response.raise_for_status()
                data = response.json()
                self.request_count["ollama"] += 1
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Ollama error: {e}. Falling back to Claude.")
            return self._call_claude(prompt, max_tokens)

    def _call_openrouter(self, prompt: str, model: str, max_tokens: int = 4000) -> str:
        """Call OpenRouter API."""
        if not self.openrouter_api_key:
            print("No OpenRouter key, falling back to Ollama")
            return self._call_ollama(prompt, "deepseek-coder:33b", max_tokens)

        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openrouter_api_key}",
                        "HTTP-Referer": "https://github.com/cfa-prep-tool",
                        "X-Title": "CFA Prep Tool"
                    },
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": max_tokens
                    }
                )
                response.raise_for_status()
                data = response.json()
                self.request_count["openrouter"] += 1
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"OpenRouter error: {e}. Falling back to Ollama.")
            return self._call_ollama(prompt, "deepseek-coder:33b", max_tokens)

    def _call_claude(self, prompt: str, max_tokens: int = 4000) -> str:
        """Call Claude API."""
        if not self.claude_client:
            raise ValueError("Claude API key not configured")

        message = self.claude_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )

        # Approximate cost calculation
        input_tokens = len(prompt) // 4  # Rough estimate
        output_tokens = len(message.content[0].text) // 4
        cost = (input_tokens * 0.003 / 1000) + (output_tokens * 0.015 / 1000)
        self.total_cost += cost

        self.request_count["anthropic"] += 1
        return message.content[0].text

    def _route_request(self, prompt: str, complexity: str, task_type: str, max_tokens: int = 4000) -> str:
        """Route request to appropriate provider."""
        provider, model = self._select_provider(complexity, task_type)

        print(f"🎯 Routing {task_type} (complexity: {complexity}) → {provider}/{model}")

        if provider == "ollama":
            return self._call_ollama(prompt, model, max_tokens)
        elif provider == "openrouter":
            return self._call_openrouter(prompt, model, max_tokens)
        else:  # anthropic
            return self._call_claude(prompt, max_tokens)

    def generate_flashcards(self, content: str, topic: str, level: str, count: int = 10) -> List[Dict]:
        """Generate flashcards with intelligent routing."""

        # Analyze complexity
        complexity = self._analyze_complexity(content, "flashcards")

        prompt = f"""You are a CFA exam preparation expert. Analyze the following content from CFA {level} on the topic of "{topic}" and generate {count} high-quality flashcards.

Each flashcard should:
1. Focus on key concepts, formulas, definitions, or important relationships
2. Have a clear, concise question on the front
3. Have a comprehensive but focused answer on the back
4. Be practical for exam preparation
5. Include difficulty level (easy, medium, hard)

Content to analyze:
{content[:4000]}

Return your response as a JSON array with this exact structure:
[
  {{
    "front": "What is the formula for present value?",
    "back": "PV = FV / (1 + r)^n, where PV is present value, FV is future value, r is discount rate, and n is number of periods",
    "difficulty": "medium",
    "tags": ["time value of money", "present value", "formula"]
  }}
]

Generate exactly {count} flashcards. Return ONLY the JSON array, no additional text."""

        try:
            response_text = self._route_request(prompt, complexity, "flashcards", max_tokens=4000)

            # Try to extract JSON if wrapped in markdown code blocks
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]

            flashcards = json.loads(response_text.strip())

            # Add level and topic to each flashcard
            for card in flashcards:
                card['level'] = level
                card['topic'] = topic

            return flashcards

        except Exception as e:
            print(f"Error generating flashcards: {e}")
            return []

    def generate_quiz_questions(self, content: str, topic: str, level: str, count: int = 5) -> List[Dict]:
        """Generate quiz questions with intelligent routing."""

        # Analyze complexity
        complexity = self._analyze_complexity(content, "quiz")

        prompt = f"""You are a CFA exam preparation expert. Analyze the following content from CFA {level} on the topic of "{topic}" and generate {count} high-quality multiple-choice questions in the CFA exam style.

Each question should:
1. Test important concepts, calculations, or applications
2. Have 3 options (A, B, C)
3. Have only ONE correct answer
4. Include a detailed explanation of why the correct answer is right and why others are wrong
5. Be realistic for CFA exam difficulty
6. Include question type and difficulty

Content to analyze:
{content[:4000]}

Return your response as a JSON array with this exact structure:
[
  {{
    "question": "An investor purchases a bond with a face value of $1,000, coupon rate of 5%, and 3 years to maturity. If the current market rate is 6%, what is the approximate bond price?",
    "option_a": "$973",
    "option_b": "$1,000",
    "option_c": "$1,027",
    "correct_answer": "A",
    "explanation": "When market rates (6%) exceed the coupon rate (5%), the bond trades at a discount. Using present value calculations: PV of coupons + PV of principal = $973. Option B is incorrect as par value only occurs when coupon rate equals market rate. Option C is wrong as this would be a premium bond.",
    "difficulty": "medium",
    "question_type": "calculation",
    "tags": ["fixed income", "bond valuation", "present value"]
  }}
]

Generate exactly {count} questions. Return ONLY the JSON array, no additional text."""

        try:
            response_text = self._route_request(prompt, complexity, "quiz", max_tokens=4000)

            # Try to extract JSON if wrapped in markdown code blocks
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]

            questions = json.loads(response_text.strip())

            # Add level and topic to each question
            for q in questions:
                q['level'] = level
                q['topic'] = topic

            return questions

        except Exception as e:
            print(f"Error generating quiz questions: {e}")
            return []

    def extract_key_concepts(self, content: str, topic: str, level: str) -> Dict:
        """Extract key concepts with intelligent routing."""

        # Usually simple extraction
        complexity = "simple" if len(content) < 2000 else "medium"

        prompt = f"""You are a CFA exam preparation expert. Analyze the following content from CFA {level} on "{topic}" and extract:

1. Key concepts (main ideas students must understand)
2. Important formulas (with explanations)
3. Learning outcome statements (what students should be able to do)
4. Common pitfalls or mistakes to avoid

Content:
{content[:4000]}

Return your response as a JSON object with this structure:
{{
  "key_concepts": ["concept 1", "concept 2", ...],
  "formulas": [
    {{"formula": "formula notation", "explanation": "what it calculates", "variables": "variable definitions"}}
  ],
  "learning_outcomes": ["outcome 1", "outcome 2", ...],
  "pitfalls": ["pitfall 1", "pitfall 2", ...]
}}

Return ONLY the JSON object, no additional text."""

        try:
            response_text = self._route_request(prompt, complexity, "concepts", max_tokens=3000)

            # Try to extract JSON if wrapped in markdown code blocks
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]

            concepts = json.loads(response_text.strip())
            concepts['level'] = level
            concepts['topic'] = topic

            return concepts

        except Exception as e:
            print(f"Error extracting concepts: {e}")
            return {}

    def get_statistics(self) -> Dict:
        """Get routing statistics and cost savings."""
        total_requests = sum(self.request_count.values())
        if total_requests == 0:
            return {
                "total_requests": 0,
                "free_percentage": 0,
                "total_cost": 0,
                "estimated_savings": 0
            }

        free_requests = self.request_count["ollama"] + self.request_count["openrouter"]
        free_percentage = (free_requests / total_requests) * 100

        # Estimate cost if all requests went to Claude
        estimated_claude_only_cost = total_requests * 0.08  # Avg $0.08 per request
        estimated_savings = estimated_claude_only_cost - self.total_cost

        return {
            "total_requests": total_requests,
            "by_provider": self.request_count,
            "free_percentage": round(free_percentage, 1),
            "total_cost": round(self.total_cost, 2),
            "estimated_cost_without_router": round(estimated_claude_only_cost, 2),
            "estimated_savings": round(estimated_savings, 2),
            "savings_percentage": round((estimated_savings / estimated_claude_only_cost * 100), 1) if estimated_claude_only_cost > 0 else 0
        }

    def print_statistics(self):
        """Print routing statistics."""
        stats = self.get_statistics()
        print("\n" + "="*60)
        print("CFA PREP TOOL - HYBRID ROUTING STATISTICS")
        print("="*60)
        print(f"Total Requests: {stats['total_requests']}")
        print(f"  Ollama (Free):    {stats['by_provider']['ollama']}")
        print(f"  OpenRouter (Free): {stats['by_provider']['openrouter']}")
        print(f"  Claude (Paid):    {stats['by_provider']['anthropic']}")
        print(f"\nFree Requests: {stats['free_percentage']}%")
        print(f"Total Cost: ${stats['total_cost']}")
        print(f"Without Router: ${stats['estimated_cost_without_router']}")
        print(f"💰 Savings: ${stats['estimated_savings']} ({stats['savings_percentage']}%)")
        print("="*60 + "\n")


def main():
    """Test the hybrid content analyzer."""
    sample_content = """
    Time Value of Money

    The time value of money (TVM) is a fundamental concept in finance that states that
    a dollar today is worth more than a dollar in the future. This is due to the potential
    earning capacity of money - money can earn interest or investment returns over time.

    Present Value (PV): The current value of a future sum of money or stream of cash flows
    given a specified rate of return.

    Formula: PV = FV / (1 + r)^n

    Where:
    - PV = Present Value
    - FV = Future Value
    - r = discount rate (or interest rate)
    - n = number of periods
    """

    try:
        analyzer = HybridContentAnalyzer()

        print("🎓 Testing Hybrid Content Analyzer for CFA Prep\n")

        print("Generating flashcards...")
        flashcards = analyzer.generate_flashcards(sample_content, "Time Value of Money", "L1", count=3)
        print(f"✅ Generated {len(flashcards)} flashcards")

        print("\nGenerating quiz questions...")
        questions = analyzer.generate_quiz_questions(sample_content, "Time Value of Money", "L1", count=2)
        print(f"✅ Generated {len(questions)} questions")

        print("\nExtracting key concepts...")
        concepts = analyzer.extract_key_concepts(sample_content, "Time Value of Money", "L1")
        print(f"✅ Extracted {len(concepts.get('key_concepts', []))} key concepts")

        # Print statistics
        analyzer.print_statistics()

    except ValueError as e:
        print(f"Error: {e}")
        print("Please configure environment variables")

if __name__ == "__main__":
    main()
