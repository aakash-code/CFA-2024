# CFA Exam Prep Tool

A comprehensive, AI-powered study tool for CFA (Chartered Financial Analyst) exam preparation. This application helps students master CFA material through intelligent flashcards, adaptive quizzes, and progress tracking.

## Features

### 1. **Intelligent Flashcards**
- Spaced repetition algorithm (SM-2) for optimal learning
- Auto-generated from your CFA study materials using Claude AI
- Track mastery and review history
- Filter by level, topic, and difficulty

### 2. **Adaptive Quiz System**
- AI-generated multiple-choice questions in CFA exam style
- Instant feedback with detailed explanations
- Smart question selection (prioritizes weak areas)
- Performance analytics and tracking

### 3. **Progress Tracking**
- Study streak tracking to maintain motivation
- Topic-by-topic mastery analysis
- Performance trends and insights
- Personalized study recommendations

### 4. **Content Generation**
- Paste any CFA content to automatically generate:
  - Flashcards with key concepts and definitions
  - Quiz questions with explanations
  - Formula sheets and learning objectives
- Powered by Claude AI (Anthropic)

### 5. **Study Analytics**
- Overall progress dashboard
- Weak topic identification
- Time spent per topic
- Quiz accuracy metrics

## Tech Stack

**Backend:**
- FastAPI (Python web framework)
- SQLAlchemy (Database ORM)
- SQLite (Database)
- Anthropic Claude API (AI content generation)
- PyPDF for PDF text extraction

**Frontend:**
- HTML5, CSS3, JavaScript (vanilla)
- Modern, responsive design
- Single-page application architecture

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Anthropic API key ([Get one here](https://console.anthropic.com/))

### Step 1: Clone the Repository

```bash
cd CFA-2024/cfa-prep-tool
```

### Step 2: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 3: Set Up Environment Variables

Create a `.env` file in the `backend` directory:

```bash
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:

```
ANTHROPIC_API_KEY=your_actual_api_key_here
```

### Step 4: Initialize Database

The database will be automatically created when you first run the application.

```bash
cd backend
python app.py
```

### Step 5: Extract Content from PDFs (Optional)

If you want to pre-process your CFA PDFs:

```bash
python pdf_extractor.py
```

This will extract text from all PDF files in the parent directory and save them to `data/extracted/`.

## Usage

### Starting the Application

1. Navigate to the backend directory:
```bash
cd backend
```

2. Run the server:
```bash
python app.py
```

Or using uvicorn directly:
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

3. Open your web browser and go to:
```
http://localhost:8000
```

### Generating Study Materials

1. Navigate to the "Generate Content" page
2. Select your CFA level (L1, L2, L3)
3. Enter a topic name (e.g., "Time Value of Money", "Ethics", "Fixed Income")
4. Paste content from your CFA study materials
5. Choose how many flashcards and quiz questions to generate
6. Click "Generate" and wait for Claude AI to create your study materials

### Studying with Flashcards

1. Go to the "Flashcards" page
2. Filter by level or topic if desired
3. Click "Due for Review" to study cards scheduled for today
4. Click on the card to flip and see the answer
5. Rate your recall (Hard, Medium, Easy)
6. The spaced repetition algorithm will schedule the next review

### Taking Quizzes

1. Navigate to the "Quiz" page
2. Select level, topic, and number of questions
3. Click "Start Quiz"
4. Answer each question
5. Get instant feedback with explanations
6. Review your results at the end

### Tracking Progress

1. View the "Dashboard" for an overview
2. Check the "Progress" page for detailed analytics
3. Monitor your study streak
4. Identify weak areas and get recommendations

## API Endpoints

### Flashcards
- `GET /api/flashcards` - Get flashcards with filters
- `GET /api/flashcards/due` - Get due flashcards
- `POST /api/flashcards` - Create a flashcard
- `POST /api/flashcards/review` - Record a review
- `GET /api/flashcards/stats` - Get statistics

### Quiz
- `GET /api/quiz/questions` - Get quiz questions
- `GET /api/quiz/random` - Get random quiz
- `POST /api/quiz/submit` - Submit answer
- `GET /api/quiz/stats` - Get quiz statistics
- `GET /api/quiz/weak-topics` - Get weak topics

### Progress
- `GET /api/progress/overall` - Overall progress
- `GET /api/progress/level/{level}` - Progress by level
- `GET /api/progress/streak` - Study streak
- `GET /api/progress/recommendations` - Get recommendations

### Content Generation
- `POST /api/generate/flashcards` - Generate flashcards
- `POST /api/generate/quiz` - Generate quiz questions

## Project Structure

```
cfa-prep-tool/
├── backend/
│   ├── app.py                 # Main FastAPI application
│   ├── models.py              # Database models
│   ├── database.py            # Database configuration
│   ├── pdf_extractor.py       # PDF text extraction
│   ├── content_analyzer.py    # Claude AI integration
│   ├── requirements.txt       # Python dependencies
│   └── services/
│       ├── flashcard_service.py
│       ├── quiz_service.py
│       └── progress_service.py
├── frontend/
│   ├── index.html
│   └── static/
│       ├── css/
│       │   └── styles.css
│       └── js/
│           └── app.js
├── data/
│   ├── extracted/            # Extracted PDF content (JSON)
│   └── cfa_prep.db          # SQLite database
└── docs/
    └── README.md
```

## Database Schema

The application uses SQLite with the following main tables:

- **cfa_content**: Stores extracted content from PDFs
- **flashcards**: Flashcard data
- **flashcard_reviews**: Review history and scheduling
- **quiz_questions**: Quiz questions
- **quiz_attempts**: Quiz attempt history
- **study_sessions**: Study session tracking
- **learning_progress**: Topic-by-topic progress

## Features Roadmap

### Current Features (v1.0)
- ✅ AI-powered flashcard generation
- ✅ Adaptive quiz system
- ✅ Spaced repetition algorithm
- ✅ Progress tracking and analytics
- ✅ Study streak tracking
- ✅ PDF content extraction

### Planned Features (v2.0)
- 📋 Formula sheet builder
- 📋 Mock exam simulator with timed sessions
- 📋 Multi-user support with authentication
- 📋 Mobile app (React Native)
- 📋 Collaborative study groups
- 📋 Export progress reports (PDF)
- 📋 Integration with popular CFA resources

## Tips for Best Results

1. **Regular Study**: Aim to review due flashcards daily to maintain your streak
2. **Quality Content**: When generating materials, paste substantial content (at least 500 words) for best results
3. **Review Weak Areas**: Check the dashboard regularly for weak topics and focus on them
4. **Mix Methods**: Alternate between flashcards and quizzes for comprehensive learning
5. **Track Progress**: Use the analytics to adjust your study plan

## Troubleshooting

### Claude API Errors
- Ensure your `ANTHROPIC_API_KEY` is correctly set in `.env`
- Check you have API credits available
- Verify internet connection

### Database Issues
- Delete `data/cfa_prep.db` to reset the database
- Check file permissions in the data directory

### PDF Extraction Issues
- Ensure PDFs are not password-protected
- Some PDFs may have complex formatting that affects extraction
- Manually copy-paste content as a workaround

## Contributing

This is a student-focused project. Contributions, suggestions, and bug reports are welcome!

## License

This project is for educational purposes. CFA® is a registered trademark of CFA Institute.

## Acknowledgments

- Powered by Claude AI (Anthropic)
- CFA Institute for the curriculum structure
- Open-source Python and JavaScript communities

## Support

For issues, questions, or suggestions:
- Create an issue on GitHub
- Check the documentation in `/docs`

---

**Happy Studying! 📚 Good luck on your CFA exam! 🎓**
