"""Content analyzer using Claude AI to generate study materials."""
import os
import json
import anthropic
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

class ContentAnalyzer:
    """Analyze CFA content and generate flashcards and quiz questions using Claude."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        self.client = anthropic.Anthropic(api_key=self.api_key)

    def generate_flashcards(self, content: str, topic: str, level: str, count: int = 10) -> List[Dict]:
        """Generate flashcards from content using Claude."""

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
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = message.content[0].text.strip()

            # Try to extract JSON if wrapped in markdown code blocks
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]

            flashcards = json.loads(response_text)

            # Add level and topic to each flashcard
            for card in flashcards:
                card['level'] = level
                card['topic'] = topic

            return flashcards

        except Exception as e:
            print(f"Error generating flashcards: {e}")
            return []

    def generate_quiz_questions(self, content: str, topic: str, level: str, count: int = 5) -> List[Dict]:
        """Generate quiz questions from content using Claude."""

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
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = message.content[0].text.strip()

            # Try to extract JSON if wrapped in markdown code blocks
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]

            questions = json.loads(response_text)

            # Add level and topic to each question
            for q in questions:
                q['level'] = level
                q['topic'] = topic

            return questions

        except Exception as e:
            print(f"Error generating quiz questions: {e}")
            return []

    def extract_key_concepts(self, content: str, topic: str, level: str) -> Dict:
        """Extract key concepts, formulas, and learning outcomes from content."""

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
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = message.content[0].text.strip()

            # Try to extract JSON if wrapped in markdown code blocks
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]

            concepts = json.loads(response_text)
            concepts['level'] = level
            concepts['topic'] = topic

            return concepts

        except Exception as e:
            print(f"Error extracting concepts: {e}")
            return {}

def main():
    """Test the content analyzer."""
    # This would be used with extracted PDF content
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
        analyzer = ContentAnalyzer()

        print("Generating flashcards...")
        flashcards = analyzer.generate_flashcards(sample_content, "Time Value of Money", "L1", count=3)
        print(f"Generated {len(flashcards)} flashcards")

        print("\nGenerating quiz questions...")
        questions = analyzer.generate_quiz_questions(sample_content, "Time Value of Money", "L1", count=2)
        print(f"Generated {len(questions)} questions")

        print("\nExtracting key concepts...")
        concepts = analyzer.extract_key_concepts(sample_content, "Time Value of Money", "L1")
        print(f"Extracted {len(concepts.get('key_concepts', []))} key concepts")

    except ValueError as e:
        print(f"Error: {e}")
        print("Please set ANTHROPIC_API_KEY environment variable")

if __name__ == "__main__":
    main()
