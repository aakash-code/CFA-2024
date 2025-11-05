# Quick Start Guide - CFA Prep Tool

Get up and running in 5 minutes!

## Prerequisites

- Python 3.8+
- Anthropic API key ([Get free credits](https://console.anthropic.com/))

## Installation (3 Steps)

### 1. Install Dependencies

```bash
cd /home/user/CFA-2024/cfa-prep-tool/backend
pip install -r requirements.txt
```

### 2. Configure API Key

Create a `.env` file in the `backend` directory:

```bash
echo "ANTHROPIC_API_KEY=your_api_key_here" > .env
```

Replace `your_api_key_here` with your actual Anthropic API key.

### 3. Start the Server

```bash
python app.py
```

That's it! Open http://localhost:8000 in your browser.

## First Steps

### Option A: Generate Content from Your CFA Materials

1. Click "Generate Content" in the sidebar
2. Paste text from any CFA chapter or reading
3. Enter the topic name (e.g., "Ethics", "Fixed Income")
4. Click "Generate Both" to create flashcards and quiz questions
5. Wait 30-60 seconds for Claude to generate your materials

### Option B: Use the PDF Extractor

If you want to process all your CFA PDFs at once:

```bash
# From the backend directory
python pdf_extractor.py
```

This extracts text from all PDFs in the parent directory and saves them to `data/extracted/`.

## Usage Examples

### Study with Flashcards

1. Go to "Flashcards" page
2. Click "Due for Review" (or "All Cards" if starting fresh)
3. Read the question and try to answer
4. Click the card to flip and see the answer
5. Rate yourself: Easy (5), Medium (3), or Hard (2)

The spaced repetition algorithm will automatically schedule your next review.

### Take a Quiz

1. Go to "Quiz" page
2. Select level and topic (optional)
3. Set number of questions (default: 10)
4. Click "Start Quiz"
5. Answer questions and get instant feedback
6. Review results and explanations

### Track Your Progress

1. Check the "Dashboard" for overview stats
2. View "Progress" page for detailed analytics
3. Monitor study streak (aim for consistency!)
4. Review weak topics and get personalized recommendations

## Sample Content for Testing

If you want to test the system without using real CFA materials:

**Sample Topic: Time Value of Money**

```
Time Value of Money (TVM)

The time value of money is one of the most fundamental concepts in finance. It states that a dollar received today is worth more than a dollar received in the future because of the opportunity to invest and earn returns.

Present Value (PV): The current value of a future sum of money or stream of cash flows given a specified rate of return. Future amounts are discounted back to the present using a discount rate.

Formula: PV = FV / (1 + r)^n

Where:
- PV = Present Value
- FV = Future Value
- r = discount rate (interest rate per period)
- n = number of periods

Future Value (FV): The value of a current sum of money at a specified date in the future, assuming a certain interest rate.

Formula: FV = PV × (1 + r)^n

Applications:
1. Investment analysis - comparing cash flows occurring at different times
2. Bond valuation - calculating the present value of future coupon payments
3. Loan amortization - determining payment schedules
4. Capital budgeting - evaluating long-term projects

Important Considerations:
- The discount rate should reflect the opportunity cost of capital
- Higher discount rates result in lower present values
- TVM is essential for Net Present Value (NPV) calculations
- Compounding frequency affects the final values
```

Paste this into the "Generate Content" page with topic "Time Value of Money" and Level "L1".

## Keyboard Shortcuts (Coming Soon)

- `Space` - Flip flashcard
- `1-5` - Rate flashcard (1=hardest, 5=easiest)
- `N` - Next question
- `P` - Previous question

## Tips for Success

1. **Study Daily**: Even 15 minutes maintains your streak
2. **Be Honest**: Rate flashcards accurately for optimal scheduling
3. **Review Weak Areas**: The dashboard shows where you need focus
4. **Mix It Up**: Alternate flashcards and quizzes
5. **Track Progress**: Use analytics to adjust your study plan

## Troubleshooting

**Server won't start?**
- Check Python version: `python --version` (needs 3.8+)
- Install dependencies: `pip install -r requirements.txt`

**Content generation fails?**
- Verify API key is set in `.env` file
- Check API credits at console.anthropic.com
- Ensure content is at least 200 words

**No data showing?**
- Generate some flashcards/quizzes first
- Check browser console for errors (F12)
- Verify backend is running (check terminal)

**Database issues?**
- Reset: `rm data/cfa_prep.db` then restart server
- Database recreates automatically

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Process your CFA PDFs with `pdf_extractor.py`
- Set up a daily study routine
- Explore all features: flashcards, quizzes, progress tracking

## Need Help?

- Check the README.md for detailed docs
- Review API endpoints for custom integrations
- Report issues on GitHub

---

**You're all set! Start studying and ace that CFA exam! 🎯**
