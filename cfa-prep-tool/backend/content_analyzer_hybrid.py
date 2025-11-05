"""Free content analyzer using local Ollama models and Finance-LLM."""
import os
import json
import httpx
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()


class HybridContentAnalyzer:
    """Analyze CFA content using 100% free local models (Ollama + Finance-LLM)."""

    def __init__(self, api_key: str = None):
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")

        # Finance-LLM configuration
        self.use_finance_llm = os.getenv("USE_FINANCE_LLM", "true").lower() == "true"
        self.finance_llm_model = os.getenv("FINANCE_LLM_MODEL", "finance-llm")
        self.finance_llm_available = False

        # Fallback models (all free local Ollama models)
        self.fallback_models = [
            "qwen2.5-coder:7b",
            "deepseek-coder:33b",
            "llama3:8b"
        ]

        # Check if finance-llm is available
        if self.use_finance_llm:
            self._check_finance_llm_availability()

        # Usage tracking (all free!)
        self.request_count = {
            "ollama": 0,
            "ollama_finance": 0  # Track finance-LLM separately
        }

    def _check_finance_llm_availability(self):
        """Check if finance-llm model is available in Ollama."""
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.ollama_base_url.replace('/v1', '')}/api/tags")
                if response.status_code == 200:
                    models = response.json().get('models', [])
                    self.finance_llm_available = any(
                        model.get('name', '').startswith(self.finance_llm_model)
                        for model in models
                    )
                    if self.finance_llm_available:
                        print(f"✓ Finance-LLM ({self.finance_llm_model}) is available")
                    else:
                        print(f"⚠ Finance-LLM ({self.finance_llm_model}) not found. Install with: setup_finance_llm.sh")
        except Exception as e:
            print(f"Could not check for finance-llm: {e}")
            self.finance_llm_available = False

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
        Select the best free local model based on complexity.
        Returns: (provider, model)
        """
        # PRIORITY: Use Finance-LLM for CFA content when available
        # Finance-LLM is specialized for financial/CFA content and provides superior quality
        if self.finance_llm_available:
            return ("ollama", self.finance_llm_model)

        # Fallback routing based on complexity (all free local models)
        if complexity == "simple":
            return ("ollama", "qwen2.5-coder:7b")
        elif complexity == "medium":
            return ("ollama", "deepseek-coder:33b")
        else:  # complex
            # For complex tasks, try deepseek-coder:33b (most powerful free model)
            return ("ollama", "deepseek-coder:33b")

    def _call_ollama(self, prompt: str, model: str, max_tokens: int = 4000) -> str:
        """Call local Ollama model with automatic fallback to other free models."""
        # Try the requested model first
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

                # Track finance-LLM usage separately
                if model == self.finance_llm_model:
                    self.request_count["ollama_finance"] += 1
                else:
                    self.request_count["ollama"] += 1

                return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"⚠ Ollama error with {model}: {e}")

            # Try fallback models (all free!)
            for fallback_model in self.fallback_models:
                if fallback_model == model:
                    continue  # Skip if it's the same model we just tried

                try:
                    print(f"🔄 Trying fallback: {fallback_model}")
                    with httpx.Client(timeout=60.0) as client:
                        response = client.post(
                            f"{self.ollama_base_url}/chat/completions",
                            json={
                                "model": fallback_model,
                                "messages": [{"role": "user", "content": prompt}],
                                "max_tokens": max_tokens,
                                "temperature": 0.7
                            }
                        )
                        response.raise_for_status()
                        data = response.json()
                        self.request_count["ollama"] += 1
                        return data["choices"][0]["message"]["content"]
                except Exception as fallback_error:
                    print(f"⚠ Fallback {fallback_model} also failed: {fallback_error}")
                    continue

            # If all models fail, raise an error
            raise Exception(f"All Ollama models failed. Please ensure Ollama is running and models are installed. Run: ollama pull {model}")

    def _route_request(self, prompt: str, complexity: str, task_type: str, max_tokens: int = 4000) -> str:
        """Route request to appropriate free local model."""
        provider, model = self._select_provider(complexity, task_type)

        print(f"🎯 Routing {task_type} (complexity: {complexity}) → {provider}/{model} (FREE)")

        # Only ollama provider supported (100% free!)
        return self._call_ollama(prompt, model, max_tokens)

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
        """Get usage statistics (100% free!)."""
        total_requests = sum(self.request_count.values())
        if total_requests == 0:
            return {
                "total_requests": 0,
                "total_cost": 0,
                "estimated_savings": 0
            }

        # Calculate what this would have cost with Claude API
        estimated_claude_cost = total_requests * 0.08  # Avg $0.08 per request

        return {
            "total_requests": total_requests,
            "by_provider": self.request_count,
            "finance_llm_requests": self.request_count["ollama_finance"],
            "other_ollama_requests": self.request_count["ollama"],
            "total_cost": 0.0,  # 100% FREE!
            "estimated_cost_with_claude": round(estimated_claude_cost, 2),
            "estimated_savings": round(estimated_claude_cost, 2),
            "savings_percentage": 100.0  # Always 100% savings!
        }

    def print_statistics(self):
        """Print usage statistics."""
        stats = self.get_statistics()
        print("\n" + "="*60)
        print("CFA PREP TOOL - 100% FREE USAGE STATISTICS")
        print("="*60)
        print(f"Total Requests: {stats['total_requests']}")
        print(f"  Finance-LLM (CFA-specialized): {stats['finance_llm_requests']}")
        print(f"  Other Ollama models:           {stats['other_ollama_requests']}")
        print(f"\nTotal Cost: $0.00 (100% FREE!)")
        print(f"Cost with Claude API: ${stats['estimated_cost_with_claude']}")
        print(f"💰 Your Savings: ${stats['estimated_savings']} ({stats['savings_percentage']}%)")
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

    except Exception as e:
        print(f"Error: {e}")
        print("Please ensure Ollama is running and models are installed")
        print("Run: ollama pull finance-llm  # or qwen2.5-coder:7b")

if __name__ == "__main__":
    main()
