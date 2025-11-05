"""Flashcard service with spaced repetition algorithm."""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from models import Flashcard, FlashcardReview, LearningProgress
from content_analyzer import ContentAnalyzer

class FlashcardService:
    """Service for managing flashcards and reviews."""

    def __init__(self, db: Session, analyzer: ContentAnalyzer = None):
        self.db = db
        self.analyzer = analyzer

    def create_flashcard(self, data: dict) -> Flashcard:
        """Create a new flashcard."""
        flashcard = Flashcard(**data)
        self.db.add(flashcard)
        self.db.commit()
        self.db.refresh(flashcard)
        return flashcard

    def create_flashcards_from_content(self, content: str, topic: str, level: str, count: int = 10) -> List[Flashcard]:
        """Generate and create flashcards from content using Claude AI."""
        if not self.analyzer:
            raise ValueError("ContentAnalyzer not initialized")

        # Generate flashcards using Claude
        flashcard_data = self.analyzer.generate_flashcards(content, topic, level, count)

        flashcards = []
        for data in flashcard_data:
            flashcard = Flashcard(
                front=data['front'],
                back=data['back'],
                level=data['level'],
                topic=data['topic'],
                difficulty=data.get('difficulty', 'medium'),
                tags=data.get('tags', [])
            )
            self.db.add(flashcard)
            flashcards.append(flashcard)

        self.db.commit()
        return flashcards

    def get_flashcards(self, level: Optional[str] = None, topic: Optional[str] = None,
                       difficulty: Optional[str] = None, limit: int = 50) -> List[Flashcard]:
        """Get flashcards with optional filters."""
        query = self.db.query(Flashcard)

        if level:
            query = query.filter(Flashcard.level == level)
        if topic:
            query = query.filter(Flashcard.topic == topic)
        if difficulty:
            query = query.filter(Flashcard.difficulty == difficulty)

        return query.order_by(Flashcard.created_at.desc()).limit(limit).all()

    def get_due_flashcards(self, user_id: str = "default_user", limit: int = 20) -> List[Flashcard]:
        """Get flashcards due for review using spaced repetition."""
        # Get all flashcards with their latest review
        subquery = self.db.query(
            FlashcardReview.flashcard_id,
            FlashcardReview.next_review
        ).filter(
            FlashcardReview.user_id == user_id
        ).distinct(
            FlashcardReview.flashcard_id
        ).subquery()

        # Get flashcards that are either new or due for review
        now = datetime.utcnow()
        flashcards = self.db.query(Flashcard).outerjoin(
            subquery,
            Flashcard.id == subquery.c.flashcard_id
        ).filter(
            (subquery.c.next_review == None) | (subquery.c.next_review <= now)
        ).limit(limit).all()

        return flashcards

    def record_review(self, flashcard_id: int, quality: int, user_id: str = "default_user") -> FlashcardReview:
        """Record a flashcard review using SM-2 algorithm.

        Quality rating (0-5):
        0 - Complete blackout
        1 - Incorrect response, but correct answer seemed familiar
        2 - Incorrect response, but correct answer seemed easy to remember
        3 - Correct response, but with difficulty
        4 - Correct response with hesitation
        5 - Perfect response
        """
        # Get last review for this flashcard
        last_review = self.db.query(FlashcardReview).filter(
            FlashcardReview.flashcard_id == flashcard_id,
            FlashcardReview.user_id == user_id
        ).order_by(FlashcardReview.reviewed_at.desc()).first()

        # Initialize values
        if last_review:
            ease_factor = last_review.ease_factor
            repetitions = last_review.repetitions
            interval = last_review.interval
        else:
            ease_factor = 2.5
            repetitions = 0
            interval = 1

        # SM-2 algorithm
        if quality < 3:
            # Reset if quality is poor
            repetitions = 0
            interval = 1
        else:
            if repetitions == 0:
                interval = 1
            elif repetitions == 1:
                interval = 6
            else:
                interval = int(interval * ease_factor)
            repetitions += 1

        # Update ease factor
        ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        ease_factor = max(1.3, ease_factor)  # Minimum ease factor

        # Calculate next review date
        next_review = datetime.utcnow() + timedelta(days=interval)

        # Create review record
        review = FlashcardReview(
            flashcard_id=flashcard_id,
            user_id=user_id,
            quality=quality,
            ease_factor=ease_factor,
            interval=interval,
            repetitions=repetitions,
            next_review=next_review
        )

        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)

        # Update learning progress
        self._update_learning_progress(flashcard_id, quality >= 4, user_id)

        return review

    def _update_learning_progress(self, flashcard_id: int, mastered: bool, user_id: str):
        """Update learning progress for a topic."""
        flashcard = self.db.query(Flashcard).filter(Flashcard.id == flashcard_id).first()
        if not flashcard:
            return

        progress = self.db.query(LearningProgress).filter(
            LearningProgress.user_id == user_id,
            LearningProgress.level == flashcard.level,
            LearningProgress.topic == flashcard.topic
        ).first()

        if not progress:
            progress = LearningProgress(
                user_id=user_id,
                level=flashcard.level,
                topic=flashcard.topic,
                cards_total=1,
                cards_mastered=1 if mastered else 0
            )
            self.db.add(progress)
        else:
            if mastered:
                progress.cards_mastered += 1

        progress.last_studied = datetime.utcnow()
        self.db.commit()

    def get_flashcard_stats(self, user_id: str = "default_user") -> dict:
        """Get statistics about flashcard reviews."""
        total_cards = self.db.query(Flashcard).count()

        total_reviews = self.db.query(FlashcardReview).filter(
            FlashcardReview.user_id == user_id
        ).count()

        due_cards = len(self.get_due_flashcards(user_id, limit=1000))

        return {
            "total_cards": total_cards,
            "total_reviews": total_reviews,
            "due_cards": due_cards
        }
