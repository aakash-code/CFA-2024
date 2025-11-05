"""Database models for CFA Prep Tool."""
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class CFAContent(Base):
    """Stores extracted CFA content from PDFs."""
    __tablename__ = "cfa_content"

    id = Column(Integer, primary_key=True, index=True)
    level = Column(String, index=True)  # L1, L2, L3
    volume = Column(Integer, index=True)  # 1-6
    topic = Column(String, index=True)
    subtopic = Column(String)
    content = Column(Text)
    content_type = Column(String)  # chapter, section, formula, definition
    page_number = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    flashcards = relationship("Flashcard", back_populates="content")
    quiz_questions = relationship("QuizQuestion", back_populates="content")

class Flashcard(Base):
    """Flashcard model for spaced repetition learning."""
    __tablename__ = "flashcards"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("cfa_content.id"))
    front = Column(Text)  # Question or concept
    back = Column(Text)  # Answer or explanation
    level = Column(String, index=True)
    topic = Column(String, index=True)
    difficulty = Column(String)  # easy, medium, hard
    tags = Column(JSON)  # List of tags
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    content = relationship("CFAContent", back_populates="flashcards")
    reviews = relationship("FlashcardReview", back_populates="flashcard")

class FlashcardReview(Base):
    """Track user's flashcard review history."""
    __tablename__ = "flashcard_reviews"

    id = Column(Integer, primary_key=True, index=True)
    flashcard_id = Column(Integer, ForeignKey("flashcards.id"))
    user_id = Column(String, default="default_user")  # For future multi-user support
    quality = Column(Integer)  # 0-5 rating (SM-2 algorithm)
    ease_factor = Column(Float, default=2.5)
    interval = Column(Integer, default=1)  # Days until next review
    repetitions = Column(Integer, default=0)
    next_review = Column(DateTime)
    reviewed_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    flashcard = relationship("Flashcard", back_populates="reviews")

class QuizQuestion(Base):
    """Quiz questions generated from CFA content."""
    __tablename__ = "quiz_questions"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("cfa_content.id"))
    question = Column(Text)
    option_a = Column(Text)
    option_b = Column(Text)
    option_c = Column(Text)
    option_d = Column(Text, nullable=True)
    correct_answer = Column(String)  # A, B, C, or D
    explanation = Column(Text)
    level = Column(String, index=True)
    topic = Column(String, index=True)
    difficulty = Column(String)  # easy, medium, hard
    question_type = Column(String)  # multiple_choice, calculation, conceptual
    tags = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    content = relationship("CFAContent", back_populates="quiz_questions")
    attempts = relationship("QuizAttempt", back_populates="question")

class QuizAttempt(Base):
    """Track user's quiz attempts."""
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("quiz_questions.id"))
    user_id = Column(String, default="default_user")
    user_answer = Column(String)  # A, B, C, or D
    is_correct = Column(Boolean)
    time_taken = Column(Integer)  # seconds
    attempted_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    question = relationship("QuizQuestion", back_populates="attempts")

class StudySession(Base):
    """Track study sessions for analytics."""
    __tablename__ = "study_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, default="default_user")
    session_type = Column(String)  # flashcard, quiz, reading
    level = Column(String)
    topic = Column(String)
    duration = Column(Integer)  # minutes
    cards_reviewed = Column(Integer, default=0)
    questions_answered = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)

class LearningProgress(Base):
    """Track overall learning progress by topic."""
    __tablename__ = "learning_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, default="default_user")
    level = Column(String, index=True)
    topic = Column(String, index=True)
    subtopic = Column(String)
    mastery_score = Column(Float, default=0.0)  # 0-100
    cards_mastered = Column(Integer, default=0)
    cards_total = Column(Integer, default=0)
    quiz_accuracy = Column(Float, default=0.0)  # percentage
    total_time_spent = Column(Integer, default=0)  # minutes
    last_studied = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
