# CFA Prep Tool - Organized Structure

## Directory Organization

Your CFA PDFs have been organized by level for easy access and processing:

```
cfa-prep-tool/
├── pdfs/                      # All CFA PDFs organized by level
│   ├── level1/               # CFA Level 1 (6 volumes)
│   │   ├── CFA L1 (V1).pdf
│   │   ├── CFA L1 (V2).pdf
│   │   ├── CFA L1 (V3).pdf
│   │   ├── CFA L1 (V4).pdf
│   │   ├── CFA L1 (V5).pdf
│   │   └── CFA L1 (V6).pdf
│   ├── level2/               # CFA Level 2 (6 volumes)
│   │   ├── CFA L2 (V1).pdf
│   │   ├── CFA L2 (V2).pdf
│   │   ├── CFA L2 (V3).pdf
│   │   ├── CFA L2 (V4).pdf
│   │   ├── CFA L2 (V5).pdf
│   │   └── CFA L2 (V6).pdf
│   └── level3/               # CFA Level 3 (6 volumes)
│       ├── CFA L3 (V1).pdf
│       ├── CFA L3 (V2).pdf
│       ├── CFA L3 (V3).pdf
│       ├── CFA L3 (V4).pdf
│       ├── CFA L3 (V5).pdf
│       └── CFA L3 (V6).pdf
├── backend/                  # Python FastAPI application
├── frontend/                 # Web interface
└── data/                     # Generated data
    ├── extracted/            # Extracted PDF content (JSON)
    └── cfa_prep.db          # SQLite database
```

## PDF Statistics

- **Total PDFs**: 18 files
- **Level 1**: 6 volumes (41 MB total)
- **Level 2**: 6 volumes (35 MB total)
- **Level 3**: 6 volumes (26 MB total)
- **Total Size**: ~102 MB

## How to Extract Content from PDFs

### Option 1: Batch Process All PDFs

Process all 18 PDFs at once:

```bash
cd backend
python batch_process_pdfs.py
```

This will:
- Extract text from all PDFs
- Identify sections and chapters
- Find formulas automatically
- Save structured JSON files in `data/extracted/`

### Option 2: Use the Web Interface

1. Start the server:
```bash
cd backend
python app.py
```

2. Open http://localhost:8000

3. Go to "Generate Content" page

4. Copy text from any PDF and paste it

5. Click "Generate Flashcards" or "Generate Quiz"

### Option 3: Process Individual Levels

If you want to process one level at a time, you can modify the batch script or manually extract:

```python
from pdf_extractor import CFAPDFExtractor

# Process Level 1 only
extractor = CFAPDFExtractor("pdfs/level1", "data/extracted")
results = extractor.process_all_pdfs()
```

## Quick Start Guide

### Step 1: Verify Setup

```bash
cd backend
python verify_setup.py
```

This checks:
- ✓ Python packages installed
- ✓ PDFs organized correctly (18 PDFs)
- ✓ Database initialized
- ✓ Directory structure
- ⚠️  API key configuration

### Step 2: Add Your API Key

Edit `backend/.env` and replace with your actual Anthropic API key:

```bash
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
```

Get your free API key from: https://console.anthropic.com/

### Step 3: Extract PDF Content (Optional but Recommended)

```bash
cd backend
python batch_process_pdfs.py
```

Expected output:
```
CFA PDF Batch Processor
=======================================================

📚 Processing L1 PDFs from level1/
  Processing: CFA L1 (V1).pdf
    ✓ 245 pages
    ✓ 12 sections
    ✓ 38 formulas

[... continues for all 18 PDFs ...]

Summary:
  • PDFs processed: 18
  • Total pages: 3,245
  • Sections extracted: 215
  • Formulas found: 428
```

### Step 4: Start the Application

```bash
cd backend
python app.py
```

Or use the startup script from the project root:
```bash
./start.sh
```

### Step 5: Open in Browser

Visit: http://localhost:8000

## Using the Application

### Generate Study Materials

1. **From Web Interface**:
   - Navigate to "Generate Content"
   - Select level (L1, L2, or L3)
   - Enter topic name
   - Paste content from PDFs
   - Click "Generate Flashcards" or "Generate Quiz"

2. **Direct Upload** (Future Enhancement):
   - Will support direct PDF upload
   - Automatic topic extraction
   - Batch generation

### Study with Flashcards

1. Go to "Flashcards" page
2. Filter by level/topic
3. Click "Due for Review" for daily practice
4. Rate each card (Easy/Medium/Hard)
5. Spaced repetition automatically schedules reviews

### Take Quizzes

1. Navigate to "Quiz" page
2. Select:
   - Level (L1, L2, L3)
   - Topic (optional)
   - Number of questions (5-50)
3. Click "Start Quiz"
4. Answer questions
5. Get instant feedback with explanations

### Track Progress

1. **Dashboard**: Overview of your study stats
2. **Progress Page**: Detailed analytics by level
3. **Study Streak**: Keep your daily streak alive!
4. **Weak Topics**: Identifies areas needing more work

## PDF Content Organization

The PDFs are organized to make it easy to:

1. **Focus on One Level**: Study L1, L2, or L3 independently
2. **Batch Processing**: Extract all content at once
3. **Selective Study**: Generate materials for specific volumes
4. **Version Control**: PDFs remain in original folders

## Extracted Content Format

When you run `batch_process_pdfs.py`, each PDF generates a JSON file:

```json
{
  "filename": "CFA L1 (V1).pdf",
  "level": "L1",
  "volume": 1,
  "total_pages": 245,
  "sections": [
    {
      "title": "READING 1: Ethics and Trust",
      "content": "..."
    }
  ],
  "formulas": [
    "PV = FV / (1 + r)^n",
    "HPR = (Ending Value - Beginning Value + Income) / Beginning Value"
  ]
}
```

## Troubleshooting

### PDFs Not Found

If you get "PDF directory not found":
```bash
# Ensure PDFs are in the correct location
ls cfa-prep-tool/pdfs/level1/
ls cfa-prep-tool/pdfs/level2/
ls cfa-prep-tool/pdfs/level3/
```

### Extraction Fails

If PDF extraction fails:
1. Check PyMuPDF is installed: `pip install PyMuPDF`
2. Ensure PDFs are not corrupted
3. Check file permissions
4. Try extracting one PDF at a time

### No Content Generated

If flashcards/quizzes aren't generated:
1. Verify API key is set in `.env`
2. Check internet connection
3. Ensure pasted content is substantial (500+ words)
4. Check Anthropic API credits

## Performance Tips

1. **Batch Processing**: Process all PDFs once, use extracted JSON many times
2. **Cache Results**: Extracted JSON files are cached for fast access
3. **Incremental Study**: Focus on one level/topic at a time
4. **Regular Backups**: Backup your `data/` folder with progress

## Next Steps

1. ✅ PDFs organized by level
2. ✅ Application setup verified
3. ⏳ Add your Anthropic API key
4. ⏳ Extract PDF content
5. ⏳ Generate study materials
6. ⏳ Start your daily study routine!

## File Size Breakdown

**Level 1** (41 MB):
- V1: 8.2 MB
- V2: 8.6 MB
- V3: 5.6 MB
- V4: 8.3 MB
- V5: 6.9 MB
- V6: 3.4 MB

**Level 2** (35 MB):
- V1: 8.3 MB
- V2: 3.5 MB
- V3: 3.0 MB
- V4: 8.2 MB
- V5: 6.8 MB
- V6: 4.8 MB

**Level 3** (26 MB):
- V1: 3.9 MB
- V2: 4.4 MB
- V3: 5.2 MB
- V4: 5.0 MB
- V5: 4.8 MB
- V6: 2.3 MB

---

**Your CFA materials are now organized and ready for efficient studying!** 📚✨
