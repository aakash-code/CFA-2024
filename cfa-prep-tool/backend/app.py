"""Main FastAPI application for CFA Prep Tool."""
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import os
from datetime import datetime

# Import database and models
from database import get_db, init_db, SessionLocal
from models import Flashcard, QuizQuestion, StudySession, LearningProgress

# Import services
from services.flashcard_service import FlashcardService
from services.quiz_service import QuizService
from services.progress_service import ProgressService
from content_analyzer import ContentAnalyzer

# Initialize FastAPI app
app = FastAPI(title="CFA Prep Tool", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
app.mount("/static", StaticFiles(directory=os.path.join(frontend_path, "static")), name="static")

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()
    print("Database initialized successfully")

# Pydantic models for request/response
class FlashcardCreate(BaseModel):
    front: str
    back: str
    level: str
    topic: str
    difficulty: Optional[str] = "medium"
    tags: Optional[List[str]] = []

class FlashcardReviewRequest(BaseModel):
    flashcard_id: int
    quality: int  # 0-5

class QuizAnswerRequest(BaseModel):
    question_id: int
    user_answer: str
    time_taken: int

class GenerateContentRequest(BaseModel):
    content: str
    topic: str
    level: str
    flashcard_count: Optional[int] = 10
    question_count: Optional[int] = 5

class StudySessionStart(BaseModel):
    session_type: str
    level: str
    topic: str

class StudySessionEnd(BaseModel):
    session_id: int
    cards_reviewed: Optional[int] = 0
    questions_answered: Optional[int] = 0
    correct_answers: Optional[int] = 0

# Root endpoint - serve frontend
@app.get("/")
def read_root():
    """Serve the main frontend page."""
    return FileResponse(os.path.join(frontend_path, "index.html"))

# ============= Flashcard Endpoints =============

@app.get("/api/flashcards")
def get_flashcards(level: Optional[str] = None, topic: Optional[str] = None,
                   difficulty: Optional[str] = None, limit: int = 50,
                   db: Session = Depends(get_db)):
    """Get flashcards with optional filters."""
    service = FlashcardService(db)
    flashcards = service.get_flashcards(level, topic, difficulty, limit)
    return {"flashcards": [
        {
            "id": f.id,
            "front": f.front,
            "back": f.back,
            "level": f.level,
            "topic": f.topic,
            "difficulty": f.difficulty,
            "tags": f.tags
        } for f in flashcards
    ]}

@app.get("/api/flashcards/due")
def get_due_flashcards(limit: int = 20, db: Session = Depends(get_db)):
    """Get flashcards due for review."""
    service = FlashcardService(db)
    flashcards = service.get_due_flashcards(limit=limit)
    return {"flashcards": [
        {
            "id": f.id,
            "front": f.front,
            "back": f.back,
            "level": f.level,
            "topic": f.topic,
            "difficulty": f.difficulty
        } for f in flashcards
    ]}

@app.post("/api/flashcards")
def create_flashcard(data: FlashcardCreate, db: Session = Depends(get_db)):
    """Create a new flashcard."""
    service = FlashcardService(db)
    flashcard = service.create_flashcard(data.dict())
    return {"message": "Flashcard created successfully", "id": flashcard.id}

@app.post("/api/flashcards/review")
def review_flashcard(review: FlashcardReviewRequest, db: Session = Depends(get_db)):
    """Record a flashcard review."""
    service = FlashcardService(db)
    result = service.record_review(review.flashcard_id, review.quality)
    return {
        "message": "Review recorded",
        "next_review": result.next_review.isoformat(),
        "interval_days": result.interval
    }

@app.get("/api/flashcards/stats")
def get_flashcard_stats(db: Session = Depends(get_db)):
    """Get flashcard statistics."""
    service = FlashcardService(db)
    return service.get_flashcard_stats()

# ============= Quiz Endpoints =============

@app.get("/api/quiz/questions")
def get_quiz_questions(level: Optional[str] = None, topic: Optional[str] = None,
                       difficulty: Optional[str] = None, limit: int = 50,
                       db: Session = Depends(get_db)):
    """Get quiz questions with optional filters."""
    service = QuizService(db)
    questions = service.get_questions(level, topic, difficulty, limit)
    return {"questions": [
        {
            "id": q.id,
            "question": q.question,
            "option_a": q.option_a,
            "option_b": q.option_b,
            "option_c": q.option_c,
            "option_d": q.option_d,
            "level": q.level,
            "topic": q.topic,
            "difficulty": q.difficulty,
            "question_type": q.question_type
        } for q in questions
    ]}

@app.get("/api/quiz/random")
def get_random_quiz(level: Optional[str] = None, topic: Optional[str] = None,
                    count: int = 10, db: Session = Depends(get_db)):
    """Get a random quiz."""
    service = QuizService(db)
    questions = service.get_random_quiz(level, topic, count)
    return {"questions": [
        {
            "id": q.id,
            "question": q.question,
            "option_a": q.option_a,
            "option_b": q.option_b,
            "option_c": q.option_c,
            "option_d": q.option_d,
            "level": q.level,
            "topic": q.topic,
            "difficulty": q.difficulty
        } for q in questions
    ]}

@app.post("/api/quiz/submit")
def submit_quiz_answer(answer: QuizAnswerRequest, db: Session = Depends(get_db)):
    """Submit an answer to a quiz question."""
    service = QuizService(db)
    result = service.submit_answer(answer.question_id, answer.user_answer, answer.time_taken)
    return result

@app.get("/api/quiz/stats")
def get_quiz_stats(level: Optional[str] = None, topic: Optional[str] = None,
                   db: Session = Depends(get_db)):
    """Get quiz statistics."""
    service = QuizService(db)
    return service.get_quiz_stats(level=level, topic=topic)

@app.get("/api/quiz/weak-topics")
def get_weak_topics(limit: int = 5, db: Session = Depends(get_db)):
    """Get topics where user needs more practice."""
    service = QuizService(db)
    return {"weak_topics": service.get_weak_topics(limit=limit)}

# ============= Progress Endpoints =============

@app.get("/api/progress/overall")
def get_overall_progress(db: Session = Depends(get_db)):
    """Get overall learning progress."""
    service = ProgressService(db)
    return service.get_overall_progress()

@app.get("/api/progress/level/{level}")
def get_progress_by_level(level: str, db: Session = Depends(get_db)):
    """Get progress by level."""
    service = ProgressService(db)
    return {"progress": service.get_progress_by_level(level)}

@app.get("/api/progress/streak")
def get_study_streak(db: Session = Depends(get_db)):
    """Get study streak information."""
    service = ProgressService(db)
    return service.get_study_streak()

@app.get("/api/progress/activity")
def get_recent_activity(days: int = 7, db: Session = Depends(get_db)):
    """Get recent study activity."""
    service = ProgressService(db)
    return {"activity": service.get_recent_activity(days=days)}

@app.get("/api/progress/trends")
def get_performance_trends(days: int = 30, db: Session = Depends(get_db)):
    """Get performance trends."""
    service = ProgressService(db)
    return service.get_performance_trends(days=days)

@app.get("/api/progress/recommendations")
def get_recommendations(db: Session = Depends(get_db)):
    """Get personalized study recommendations."""
    service = ProgressService(db)
    return service.get_recommendations()

@app.post("/api/study-session/start")
def start_study_session(session: StudySessionStart, db: Session = Depends(get_db)):
    """Start a study session."""
    service = ProgressService(db)
    result = service.start_study_session(session.session_type, session.level, session.topic)
    return {"session_id": result.id, "started_at": result.started_at.isoformat()}

@app.post("/api/study-session/end")
def end_study_session(session: StudySessionEnd, db: Session = Depends(get_db)):
    """End a study session."""
    service = ProgressService(db)
    result = service.end_study_session(
        session.session_id,
        session.cards_reviewed,
        session.questions_answered,
        session.correct_answers
    )
    return {
        "duration": result.duration,
        "ended_at": result.ended_at.isoformat()
    }

# ============= Content Generation Endpoints =============

@app.post("/api/generate/flashcards")
def generate_flashcards(request: GenerateContentRequest, db: Session = Depends(get_db)):
    """Generate flashcards from content using Claude AI."""
    try:
        analyzer = ContentAnalyzer()
        service = FlashcardService(db, analyzer)
        flashcards = service.create_flashcards_from_content(
            request.content,
            request.topic,
            request.level,
            request.flashcard_count
        )
        return {
            "message": f"Generated {len(flashcards)} flashcards",
            "count": len(flashcards)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/generate/quiz")
def generate_quiz(request: GenerateContentRequest, db: Session = Depends(get_db)):
    """Generate quiz questions from content using Claude AI."""
    try:
        analyzer = ContentAnalyzer()
        service = QuizService(db, analyzer)
        questions = service.create_quiz_from_content(
            request.content,
            request.topic,
            request.level,
            request.question_count
        )
        return {
            "message": f"Generated {len(questions)} questions",
            "count": len(questions)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============= Utility Endpoints =============

@app.get("/api/topics")
def get_available_topics(db: Session = Depends(get_db)):
    """Get all available topics and levels."""
    flashcard_topics = db.query(Flashcard.level, Flashcard.topic).distinct().all()
    quiz_topics = db.query(QuizQuestion.level, QuizQuestion.topic).distinct().all()

    all_topics = set(flashcard_topics + quiz_topics)

    # Organize by level
    topics_by_level = {"L1": [], "L2": [], "L3": []}
    for level, topic in all_topics:
        if level in topics_by_level:
            topics_by_level[level].append(topic)

    return {"topics": topics_by_level}

@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
