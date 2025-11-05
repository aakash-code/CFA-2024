"""Progress tracking and analytics service."""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from models import (
    LearningProgress, StudySession, FlashcardReview,
    QuizAttempt, QuizQuestion, Flashcard
)

class ProgressService:
    """Service for tracking and analyzing learning progress."""

    def __init__(self, db: Session):
        self.db = db

    def start_study_session(self, session_type: str, level: str, topic: str,
                           user_id: str = "default_user") -> StudySession:
        """Start a new study session."""
        session = StudySession(
            user_id=user_id,
            session_type=session_type,
            level=level,
            topic=topic,
            started_at=datetime.utcnow()
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def end_study_session(self, session_id: int, cards_reviewed: int = 0,
                         questions_answered: int = 0, correct_answers: int = 0) -> StudySession:
        """End a study session and record statistics."""
        session = self.db.query(StudySession).filter(StudySession.id == session_id).first()

        if not session:
            raise ValueError("Session not found")

        session.ended_at = datetime.utcnow()
        session.duration = int((session.ended_at - session.started_at).total_seconds() / 60)
        session.cards_reviewed = cards_reviewed
        session.questions_answered = questions_answered
        session.correct_answers = correct_answers

        # Update total time in learning progress
        progress = self.db.query(LearningProgress).filter(
            LearningProgress.user_id == session.user_id,
            LearningProgress.level == session.level,
            LearningProgress.topic == session.topic
        ).first()

        if progress:
            progress.total_time_spent += session.duration
            progress.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(session)
        return session

    def get_overall_progress(self, user_id: str = "default_user") -> Dict:
        """Get overall learning progress across all topics."""
        progress_items = self.db.query(LearningProgress).filter(
            LearningProgress.user_id == user_id
        ).all()

        if not progress_items:
            return {
                "total_topics": 0,
                "average_mastery": 0,
                "total_time_spent": 0,
                "cards_mastered": 0,
                "quiz_accuracy": 0
            }

        total_topics = len(progress_items)
        avg_mastery = sum(p.mastery_score for p in progress_items) / total_topics
        total_time = sum(p.total_time_spent for p in progress_items)
        total_cards = sum(p.cards_mastered for p in progress_items)

        # Calculate overall quiz accuracy
        total_attempts = self.db.query(QuizAttempt).filter(
            QuizAttempt.user_id == user_id
        ).count()

        correct_attempts = self.db.query(QuizAttempt).filter(
            QuizAttempt.user_id == user_id,
            QuizAttempt.is_correct == True
        ).count()

        quiz_accuracy = (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0

        return {
            "total_topics": total_topics,
            "average_mastery": round(avg_mastery, 2),
            "total_time_spent": total_time,
            "cards_mastered": total_cards,
            "quiz_accuracy": round(quiz_accuracy, 2),
            "total_quiz_attempts": total_attempts
        }

    def get_progress_by_level(self, level: str, user_id: str = "default_user") -> List[Dict]:
        """Get progress breakdown by topic for a specific level."""
        progress_items = self.db.query(LearningProgress).filter(
            LearningProgress.user_id == user_id,
            LearningProgress.level == level
        ).order_by(desc(LearningProgress.last_studied)).all()

        return [{
            "topic": p.topic,
            "mastery_score": p.mastery_score,
            "quiz_accuracy": p.quiz_accuracy,
            "cards_mastered": p.cards_mastered,
            "cards_total": p.cards_total,
            "time_spent": p.total_time_spent,
            "last_studied": p.last_studied.isoformat() if p.last_studied else None
        } for p in progress_items]

    def get_study_streak(self, user_id: str = "default_user") -> Dict:
        """Calculate study streak (consecutive days studied)."""
        sessions = self.db.query(StudySession).filter(
            StudySession.user_id == user_id,
            StudySession.ended_at != None
        ).order_by(desc(StudySession.started_at)).all()

        if not sessions:
            return {"current_streak": 0, "longest_streak": 0, "total_study_days": 0}

        # Get unique study dates
        study_dates = sorted(set(s.started_at.date() for s in sessions), reverse=True)

        # Calculate current streak
        current_streak = 0
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)

        if study_dates and (study_dates[0] == today or study_dates[0] == yesterday):
            current_date = study_dates[0]
            for date in study_dates:
                if date == current_date:
                    current_streak += 1
                    current_date -= timedelta(days=1)
                elif date == current_date:
                    continue
                else:
                    break

        # Calculate longest streak
        longest_streak = 1
        temp_streak = 1

        for i in range(1, len(study_dates)):
            if (study_dates[i-1] - study_dates[i]).days == 1:
                temp_streak += 1
                longest_streak = max(longest_streak, temp_streak)
            else:
                temp_streak = 1

        return {
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "total_study_days": len(study_dates)
        }

    def get_recent_activity(self, user_id: str = "default_user", days: int = 7) -> List[Dict]:
        """Get recent study activity."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        sessions = self.db.query(StudySession).filter(
            StudySession.user_id == user_id,
            StudySession.started_at >= cutoff_date
        ).order_by(desc(StudySession.started_at)).all()

        return [{
            "date": s.started_at.isoformat(),
            "session_type": s.session_type,
            "level": s.level,
            "topic": s.topic,
            "duration": s.duration,
            "cards_reviewed": s.cards_reviewed,
            "questions_answered": s.questions_answered,
            "accuracy": round((s.correct_answers / s.questions_answered * 100), 2) if s.questions_answered > 0 else None
        } for s in sessions]

    def get_performance_trends(self, user_id: str = "default_user", days: int = 30) -> Dict:
        """Get performance trends over time."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Get quiz attempts over time
        attempts = self.db.query(
            func.date(QuizAttempt.attempted_at).label('date'),
            func.count(QuizAttempt.id).label('total'),
            func.sum(func.cast(QuizAttempt.is_correct, func.Integer)).label('correct')
        ).filter(
            QuizAttempt.user_id == user_id,
            QuizAttempt.attempted_at >= cutoff_date
        ).group_by(
            func.date(QuizAttempt.attempted_at)
        ).all()

        daily_performance = [{
            "date": str(attempt.date),
            "total_questions": attempt.total,
            "correct_answers": attempt.correct or 0,
            "accuracy": round((attempt.correct or 0) / attempt.total * 100, 2)
        } for attempt in attempts]

        # Get study time over time
        study_time = self.db.query(
            func.date(StudySession.started_at).label('date'),
            func.sum(StudySession.duration).label('total_minutes')
        ).filter(
            StudySession.user_id == user_id,
            StudySession.started_at >= cutoff_date,
            StudySession.ended_at != None
        ).group_by(
            func.date(StudySession.started_at)
        ).all()

        daily_study_time = [{
            "date": str(time.date),
            "minutes": time.total_minutes or 0
        } for time in study_time]

        return {
            "quiz_performance": daily_performance,
            "study_time": daily_study_time
        }

    def get_recommendations(self, user_id: str = "default_user") -> Dict:
        """Get personalized study recommendations."""
        # Get weak topics (low accuracy)
        weak_topics = self.db.query(LearningProgress).filter(
            LearningProgress.user_id == user_id,
            LearningProgress.quiz_accuracy < 70
        ).order_by(LearningProgress.quiz_accuracy.asc()).limit(3).all()

        # Get unstudied topics (never studied or studied long ago)
        all_progress = self.db.query(LearningProgress).filter(
            LearningProgress.user_id == user_id
        ).all()

        # Get available topics from flashcards and questions
        available_topics = set()
        for flashcard in self.db.query(Flashcard.level, Flashcard.topic).distinct().all():
            available_topics.add((flashcard.level, flashcard.topic))

        studied_topics = {(p.level, p.topic) for p in all_progress}
        unstudied = list(available_topics - studied_topics)[:3]

        # Get due flashcards
        due_cards_count = self.db.query(FlashcardReview).filter(
            FlashcardReview.user_id == user_id,
            FlashcardReview.next_review <= datetime.utcnow()
        ).count()

        return {
            "weak_topics": [{
                "level": t.level,
                "topic": t.topic,
                "accuracy": t.quiz_accuracy,
                "recommendation": "Focus on practice questions"
            } for t in weak_topics],
            "unstudied_topics": [{
                "level": t[0],
                "topic": t[1],
                "recommendation": "Start with flashcards"
            } for t in unstudied[:3]],
            "due_flashcards": due_cards_count,
            "recommendation_summary": self._generate_recommendation_summary(weak_topics, due_cards_count)
        }

    def _generate_recommendation_summary(self, weak_topics, due_cards_count) -> str:
        """Generate a summary recommendation message."""
        recommendations = []

        if due_cards_count > 0:
            recommendations.append(f"Review {due_cards_count} due flashcards")

        if weak_topics:
            topic_names = ", ".join([t.topic for t in weak_topics[:2]])
            recommendations.append(f"Practice more questions on: {topic_names}")

        if not recommendations:
            recommendations.append("Great progress! Continue with your study plan")

        return ". ".join(recommendations)
