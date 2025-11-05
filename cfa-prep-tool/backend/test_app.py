"""Test script to verify the application setup."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import fitz  # PyMuPDF
        print("✓ All required packages imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_database():
    """Test database initialization."""
    print("\nTesting database setup...")
    try:
        from database import init_db, SessionLocal, engine
        from models import Base

        # Initialize database
        init_db()
        print("✓ Database initialized successfully")

        # Test session
        db = SessionLocal()
        db.close()
        print("✓ Database session created successfully")

        # Check tables
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"✓ Created {len(tables)} tables: {', '.join(tables)}")

        return True
    except Exception as e:
        print(f"✗ Database error: {e}")
        return False

def test_models():
    """Test that models can be created."""
    print("\nTesting models...")
    try:
        from models import Flashcard, QuizQuestion, LearningProgress
        from database import SessionLocal

        db = SessionLocal()

        # Create a test flashcard
        flashcard = Flashcard(
            front="What is the formula for Present Value?",
            back="PV = FV / (1 + r)^n",
            level="L1",
            topic="Time Value of Money",
            difficulty="medium",
            tags=["formula", "TVM"]
        )
        db.add(flashcard)
        db.commit()

        # Query it back
        result = db.query(Flashcard).filter(Flashcard.topic == "Time Value of Money").first()
        assert result is not None
        print(f"✓ Created and retrieved test flashcard (ID: {result.id})")

        db.close()
        return True
    except Exception as e:
        print(f"✗ Model error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_services():
    """Test service layer."""
    print("\nTesting services...")
    try:
        from services.flashcard_service import FlashcardService
        from services.quiz_service import QuizService
        from services.progress_service import ProgressService
        from database import SessionLocal

        db = SessionLocal()

        # Test FlashcardService
        fc_service = FlashcardService(db)
        stats = fc_service.get_flashcard_stats()
        print(f"✓ FlashcardService: {stats['total_cards']} cards")

        # Test QuizService
        quiz_service = QuizService(db)
        stats = quiz_service.get_quiz_stats()
        print(f"✓ QuizService: {stats['total_attempts']} attempts")

        # Test ProgressService
        progress_service = ProgressService(db)
        progress = progress_service.get_overall_progress()
        print(f"✓ ProgressService: {progress['total_topics']} topics")

        db.close()
        return True
    except Exception as e:
        print(f"✗ Service error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_health():
    """Test that FastAPI app can be created."""
    print("\nTesting FastAPI app...")
    try:
        from app import app
        from fastapi.testclient import TestClient

        client = TestClient(app)
        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()
        print(f"✓ API health check passed: {data['status']}")

        return True
    except Exception as e:
        print(f"✗ API error: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("CFA Prep Tool - System Test")
    print("=" * 60)

    results = []

    results.append(("Imports", test_imports()))
    results.append(("Database", test_database()))
    results.append(("Models", test_models()))
    results.append(("Services", test_services()))
    results.append(("API", test_api_health()))

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{name:15} {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! The application is ready to use.")
        print("\nTo start the server, run:")
        print("  python app.py")
        print("\nThen open http://localhost:8000 in your browser.")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")

    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
