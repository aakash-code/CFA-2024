"""Quiz service for generating and managing quizzes."""
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict
import sys
import os
import random
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from models import QuizQuestion, QuizAttempt, LearningProgress, StudySession
from content_analyzer_hybrid import HybridContentAnalyzer as ContentAnalyzer

class QuizService:
    """Service for managing quizzes and quiz attempts."""

    def __init__(self, db: Session, analyzer: ContentAnalyzer = None):
        self.db = db
        self.analyzer = analyzer

    def create_quiz_question(self, data: dict) -> QuizQuestion:
        """Create a new quiz question."""
        question = QuizQuestion(**data)
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        return question

    def create_quiz_from_content(self, content: str, topic: str, level: str, count: int = 5) -> List[QuizQuestion]:
        """Generate and create quiz questions from content using Claude AI."""
        if not self.analyzer:
            raise ValueError("ContentAnalyzer not initialized")

        # Generate questions using Claude
        question_data = self.analyzer.generate_quiz_questions(content, topic, level, count)

        questions = []
        for data in question_data:
            question = QuizQuestion(
                question=data['question'],
                option_a=data['option_a'],
                option_b=data['option_b'],
                option_c=data['option_c'],
                option_d=data.get('option_d'),
                correct_answer=data['correct_answer'],
                explanation=data['explanation'],
                level=data['level'],
                topic=data['topic'],
                difficulty=data.get('difficulty', 'medium'),
                question_type=data.get('question_type', 'multiple_choice'),
                tags=data.get('tags', [])
            )
            self.db.add(question)
            questions.append(question)

        self.db.commit()
        return questions

    def get_questions(self, level: Optional[str] = None, topic: Optional[str] = None,
                     difficulty: Optional[str] = None, limit: int = 50) -> List[QuizQuestion]:
        """Get quiz questions with optional filters."""
        query = self.db.query(QuizQuestion)

        if level:
            query = query.filter(QuizQuestion.level == level)
        if topic:
            query = query.filter(QuizQuestion.topic == topic)
        if difficulty:
            query = query.filter(QuizQuestion.difficulty == difficulty)

        return query.order_by(QuizQuestion.created_at.desc()).limit(limit).all()

    def get_random_quiz(self, level: Optional[str] = None, topic: Optional[str] = None,
                       count: int = 10, user_id: str = "default_user") -> List[QuizQuestion]:
        """Get random quiz questions, prioritizing unanswered or incorrectly answered questions."""
        query = self.db.query(QuizQuestion)

        if level:
            query = query.filter(QuizQuestion.level == level)
        if topic:
            query = query.filter(QuizQuestion.topic == topic)

        # Get all questions
        all_questions = query.all()

        if not all_questions:
            return []

        # Get user's attempt history
        attempted_ids = {attempt.question_id for attempt in self.db.query(QuizAttempt).filter(
            QuizAttempt.user_id == user_id
        ).all()}

        # Prioritize unattempted questions
        unattempted = [q for q in all_questions if q.id not in attempted_ids]

        # Get incorrectly answered questions
        incorrect = [q for q in all_questions if q.id in attempted_ids and
                    self.db.query(QuizAttempt).filter(
                        QuizAttempt.question_id == q.id,
                        QuizAttempt.user_id == user_id,
                        QuizAttempt.is_correct == False
                    ).first()]

        # Mix questions: 50% unattempted, 30% incorrect, 20% all
        quiz_questions = []

        if len(unattempted) > 0:
            quiz_questions.extend(random.sample(unattempted, min(count // 2, len(unattempted))))

        remaining = count - len(quiz_questions)
        if remaining > 0 and len(incorrect) > 0:
            quiz_questions.extend(random.sample(incorrect, min(remaining // 2, len(incorrect))))

        remaining = count - len(quiz_questions)
        if remaining > 0:
            other = [q for q in all_questions if q not in quiz_questions]
            if other:
                quiz_questions.extend(random.sample(other, min(remaining, len(other))))

        random.shuffle(quiz_questions)
        return quiz_questions[:count]

    def submit_answer(self, question_id: int, user_answer: str,
                     time_taken: int, user_id: str = "default_user") -> Dict:
        """Submit an answer to a quiz question and return result."""
        question = self.db.query(QuizQuestion).filter(QuizQuestion.id == question_id).first()

        if not question:
            raise ValueError("Question not found")

        is_correct = user_answer.upper() == question.correct_answer.upper()

        # Record attempt
        attempt = QuizAttempt(
            question_id=question_id,
            user_id=user_id,
            user_answer=user_answer.upper(),
            is_correct=is_correct,
            time_taken=time_taken
        )

        self.db.add(attempt)
        self.db.commit()

        # Update learning progress
        self._update_learning_progress(question, is_correct, user_id)

        return {
            "is_correct": is_correct,
            "correct_answer": question.correct_answer,
            "explanation": question.explanation,
            "user_answer": user_answer.upper()
        }

    def _update_learning_progress(self, question: QuizQuestion, is_correct: bool, user_id: str):
        """Update learning progress for a topic."""
        progress = self.db.query(LearningProgress).filter(
            LearningProgress.user_id == user_id,
            LearningProgress.level == question.level,
            LearningProgress.topic == question.topic
        ).first()

        if not progress:
            progress = LearningProgress(
                user_id=user_id,
                level=question.level,
                topic=question.topic
            )
            self.db.add(progress)

        # Update quiz accuracy
        total_attempts = self.db.query(QuizAttempt).join(QuizQuestion).filter(
            QuizAttempt.user_id == user_id,
            QuizQuestion.level == question.level,
            QuizQuestion.topic == question.topic
        ).count()

        correct_attempts = self.db.query(QuizAttempt).join(QuizQuestion).filter(
            QuizAttempt.user_id == user_id,
            QuizAttempt.is_correct == True,
            QuizQuestion.level == question.level,
            QuizQuestion.topic == question.topic
        ).count()

        if total_attempts > 0:
            progress.quiz_accuracy = (correct_attempts / total_attempts) * 100

        progress.last_studied = datetime.utcnow()
        self.db.commit()

    def get_quiz_stats(self, user_id: str = "default_user", level: Optional[str] = None,
                       topic: Optional[str] = None) -> Dict:
        """Get quiz statistics for a user."""
        query = self.db.query(QuizAttempt).join(QuizQuestion)

        if user_id:
            query = query.filter(QuizAttempt.user_id == user_id)
        if level:
            query = query.filter(QuizQuestion.level == level)
        if topic:
            query = query.filter(QuizQuestion.topic == topic)

        total_attempts = query.count()
        correct_attempts = query.filter(QuizAttempt.is_correct == True).count()

        accuracy = (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0

        # Get average time per question
        avg_time = self.db.query(func.avg(QuizAttempt.time_taken)).filter(
            QuizAttempt.user_id == user_id
        ).scalar() or 0

        return {
            "total_attempts": total_attempts,
            "correct_attempts": correct_attempts,
            "accuracy": round(accuracy, 2),
            "average_time": round(avg_time, 2)
        }

    def get_weak_topics(self, user_id: str = "default_user", limit: int = 5) -> List[Dict]:
        """Identify topics where the user needs more practice."""
        progress_items = self.db.query(LearningProgress).filter(
            LearningProgress.user_id == user_id
        ).order_by(LearningProgress.quiz_accuracy.asc()).limit(limit).all()

        return [{
            "level": p.level,
            "topic": p.topic,
            "accuracy": p.quiz_accuracy,
            "cards_mastered": p.cards_mastered,
            "cards_total": p.cards_total
        } for p in progress_items]
