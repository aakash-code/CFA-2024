#!/usr/bin/env python3
"""
Bulk content processor for CFA-I repository integration.
Automatically generates flashcards and quizzes from extracted notebook content.
"""
import json
import os
import sys
from pathlib import Path
from typing import List, Dict
import time

# Add parent directory to path for imports
sys.path.append(os.path.dirname(__file__))

from content_analyzer_hybrid import HybridContentAnalyzer
from database import SessionLocal, init_db
from models import Flashcard, QuizQuestion

class BulkContentGenerator:
    """Generate flashcards and quizzes in bulk from CFA content."""

    def __init__(self, content_file: str):
        """Initialize with extracted content file."""
        self.content_file = Path(content_file)
        self.analyzer = HybridContentAnalyzer()
        self.db = SessionLocal()

        # Initialize database
        init_db()

        # Load content
        with open(self.content_file, 'r', encoding='utf-8') as f:
            self.notebooks = json.load(f)

        print(f"✓ Loaded {len(self.notebooks)} notebooks")

    def determine_topic_and_level(self, notebook_title: str) -> tuple[str, str]:
        """Determine CFA topic and level from notebook title."""
        # Map notebook titles to CFA topics
        topic_mapping = {
            'quantitative': 'Quantitative Methods',
            'economics': 'Economics',
            'financial reporting': 'Financial Reporting and Analysis',
            'corporate finance': 'Corporate Finance',
            'equity': 'Equity Investments',
            'fixed income': 'Fixed Income',
            'derivatives': 'Derivatives',
            'alternative': 'Alternative Investments',
            'portfolio': 'Portfolio Management',
            'ethics': 'Ethical and Professional Standards'
        }

        title_lower = notebook_title.lower()

        for key, topic in topic_mapping.items():
            if key in title_lower:
                return (topic, 'L1')  # CFA-I repository is Level 1

        return ('General', 'L1')

    def generate_from_notebook(self, notebook: Dict, flashcard_count: int = 10, quiz_count: int = 5):
        """Generate flashcards and quizzes from a single notebook."""
        title = notebook['title']
        full_text = notebook['full_text']

        # Skip if no content
        if len(full_text.strip()) < 100:
            print(f"  ⚠ Skipping {title} - insufficient content")
            return None

        topic, level = self.determine_topic_and_level(title)

        print(f"\n📘 Processing: {title}")
        print(f"   Topic: {topic} | Level: {level}")
        print(f"   Content: {len(full_text):,} characters")

        results = {
            'title': title,
            'topic': topic,
            'level': level,
            'flashcards': [],
            'quizzes': []
        }

        # Generate flashcards
        try:
            print(f"   🎴 Generating {flashcard_count} flashcards...")
            flashcards_data = self.analyzer.generate_flashcards(
                content=full_text,
                topic=topic,
                level=level,
                count=flashcard_count
            )

            # Save to database
            for fc_data in flashcards_data:
                flashcard = Flashcard(
                    front=fc_data['front'],
                    back=fc_data['back'],
                    topic=fc_data['topic'],
                    level=fc_data['level'],
                    difficulty=fc_data.get('difficulty', 'medium'),
                    tags=','.join(fc_data.get('tags', []))
                )
                self.db.add(flashcard)
                results['flashcards'].append(fc_data)

            self.db.commit()
            print(f"   ✓ Created {len(flashcards_data)} flashcards")

        except Exception as e:
            print(f"   ✗ Error generating flashcards: {e}")
            self.db.rollback()

        # Generate quiz questions
        try:
            print(f"   📝 Generating {quiz_count} quiz questions...")
            quiz_data = self.analyzer.generate_quiz_questions(
                content=full_text,
                topic=topic,
                level=level,
                count=quiz_count
            )

            # Save to database
            for q_data in quiz_data:
                question = QuizQuestion(
                    question=q_data['question'],
                    option_a=q_data['option_a'],
                    option_b=q_data['option_b'],
                    option_c=q_data['option_c'],
                    correct_answer=q_data['correct_answer'],
                    explanation=q_data['explanation'],
                    topic=q_data['topic'],
                    level=q_data['level'],
                    difficulty=q_data.get('difficulty', 'medium'),
                    question_type=q_data.get('question_type', 'conceptual'),
                    tags=','.join(q_data.get('tags', []))
                )
                self.db.add(question)
                results['quizzes'].append(q_data)

            self.db.commit()
            print(f"   ✓ Created {len(quiz_data)} quiz questions")

        except Exception as e:
            print(f"   ✗ Error generating quizzes: {e}")
            self.db.rollback()

        # Small delay to not overwhelm Ollama
        time.sleep(2)

        return results

    def process_all_notebooks(self, flashcards_per_notebook: int = 10, quizzes_per_notebook: int = 5, limit: int = None):
        """Process all notebooks and generate study materials."""
        print("\n" + "="*60)
        print("CFA-I BULK CONTENT GENERATION")
        print("="*60)
        print(f"Notebooks to process: {len(self.notebooks) if not limit else min(limit, len(self.notebooks))}")
        print(f"Flashcards per notebook: {flashcards_per_notebook}")
        print(f"Quizzes per notebook: {quizzes_per_notebook}")
        print("="*60)

        all_results = []
        total_flashcards = 0
        total_quizzes = 0

        notebooks_to_process = self.notebooks[:limit] if limit else self.notebooks

        for i, notebook in enumerate(notebooks_to_process, 1):
            print(f"\n[{i}/{len(notebooks_to_process)}] ", end='')

            result = self.generate_from_notebook(
                notebook,
                flashcard_count=flashcards_per_notebook,
                quiz_count=quizzes_per_notebook
            )

            if result:
                all_results.append(result)
                total_flashcards += len(result['flashcards'])
                total_quizzes += len(result['quizzes'])

        # Print summary
        print("\n" + "="*60)
        print("GENERATION COMPLETE!")
        print("="*60)
        print(f"✓ Processed notebooks: {len(all_results)}")
        print(f"✓ Total flashcards created: {total_flashcards}")
        print(f"✓ Total quiz questions created: {total_quizzes}")
        print("="*60)

        # Show statistics
        self.analyzer.print_statistics()

        # Save results summary
        summary_file = self.content_file.parent / 'generation_summary.json'
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump({
                'total_notebooks': len(all_results),
                'total_flashcards': total_flashcards,
                'total_quizzes': total_quizzes,
                'results': all_results
            }, f, indent=2)

        print(f"\n✓ Summary saved to: {summary_file}")

        return all_results

    def close(self):
        """Close database connection."""
        self.db.close()

def main():
    """Main function with command-line interface."""
    import argparse

    parser = argparse.ArgumentParser(description='Bulk generate CFA study materials from notebooks')
    parser.add_argument('--content-file', default='../cfa-content/extracted_content.json',
                        help='Path to extracted content JSON file')
    parser.add_argument('--flashcards', type=int, default=10,
                        help='Number of flashcards per notebook (default: 10)')
    parser.add_argument('--quizzes', type=int, default=5,
                        help='Number of quiz questions per notebook (default: 5)')
    parser.add_argument('--limit', type=int, default=None,
                        help='Limit number of notebooks to process (for testing)')

    args = parser.parse_args()

    # Check if content file exists
    if not os.path.exists(args.content_file):
        print(f"✗ Error: Content file not found: {args.content_file}")
        print("\nPlease run: python process_cfa_notebooks.py first")
        sys.exit(1)

    # Create generator
    generator = BulkContentGenerator(args.content_file)

    try:
        # Process notebooks
        generator.process_all_notebooks(
            flashcards_per_notebook=args.flashcards,
            quizzes_per_notebook=args.quizzes,
            limit=args.limit
        )
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user")
    finally:
        generator.close()

    print("\n✓ You can now use the CFA Prep Tool to review your flashcards and quizzes!")
    print("  Start the app: python app.py")
    print("  Open: http://localhost:8000")

if __name__ == '__main__':
    main()
