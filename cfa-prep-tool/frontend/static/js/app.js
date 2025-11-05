// CFA Prep Tool - Frontend JavaScript

const API_BASE = '';

// State management
let currentFlashcards = [];
let currentFlashcardIndex = 0;
let currentQuiz = [];
let currentQuestionIndex = 0;
let quizAnswers = [];
let quizStartTime = null;
let currentSessionId = null;

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    setupNavigation();
    loadDashboard();
    loadTopics();
    loadFlashcardStats();
    loadQuizStats();
});

// Navigation
function setupNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const page = this.dataset.page;
            showPage(page);

            // Update active state
            navLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
        });
    });
}

function showPage(pageName) {
    const pages = document.querySelectorAll('.page');
    pages.forEach(page => page.classList.remove('active'));

    const targetPage = document.getElementById(`${pageName}-page`);
    if (targetPage) {
        targetPage.classList.add('active');

        // Load page-specific data
        if (pageName === 'dashboard') loadDashboard();
        if (pageName === 'progress') loadProgress();
    }
}

// Dashboard
async function loadDashboard() {
    try {
        const [progress, streak, recommendations, weakTopics] = await Promise.all([
            fetch(`${API_BASE}/api/progress/overall`).then(r => r.json()),
            fetch(`${API_BASE}/api/progress/streak`).then(r => r.json()),
            fetch(`${API_BASE}/api/progress/recommendations`).then(r => r.json()),
            fetch(`${API_BASE}/api/quiz/weak-topics`).then(r => r.json())
        ]);

        // Update stats
        document.getElementById('total-topics').textContent = progress.total_topics;
        document.getElementById('quiz-accuracy').textContent = `${progress.quiz_accuracy}%`;
        document.getElementById('total-time').textContent = Math.round(progress.total_time_spent / 60);
        document.getElementById('cards-mastered').textContent = progress.cards_mastered;

        // Update streak
        document.querySelector('.streak-count').textContent = streak.current_streak;

        // Display recommendations
        displayRecommendations(recommendations);

        // Display weak topics
        displayWeakTopics(weakTopics.weak_topics);

    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

function displayRecommendations(recommendations) {
    const container = document.getElementById('recommendations-container');
    if (recommendations.recommendation_summary) {
        container.innerHTML = `
            <div class="recommendation-item">
                <p>${recommendations.recommendation_summary}</p>
            </div>
        `;
    } else {
        container.innerHTML = '<p>No recommendations at this time.</p>';
    }
}

function displayWeakTopics(topics) {
    const container = document.getElementById('weak-topics-container');
    if (topics && topics.length > 0) {
        container.innerHTML = topics.map(topic => `
            <div class="topic-item">
                <strong>${topic.level} - ${topic.topic}</strong>
                <p>Accuracy: ${topic.accuracy.toFixed(1)}% | ${topic.recommendation}</p>
            </div>
        `).join('');
    } else {
        container.innerHTML = '<p>No weak topics identified yet. Keep studying!</p>';
    }
}

// Flashcards
async function loadFlashcardStats() {
    try {
        const stats = await fetch(`${API_BASE}/api/flashcards/stats`).then(r => r.json());
        document.getElementById('fc-total').textContent = stats.total_cards;
        document.getElementById('fc-due').textContent = stats.due_cards;
        document.getElementById('fc-reviews').textContent = stats.total_reviews;
    } catch (error) {
        console.error('Error loading flashcard stats:', error);
    }
}

async function loadDueFlashcards() {
    showLoading(true);
    try {
        const response = await fetch(`${API_BASE}/api/flashcards/due?limit=20`);
        const data = await response.json();
        currentFlashcards = data.flashcards;
        currentFlashcardIndex = 0;

        if (currentFlashcards.length === 0) {
            showMessage('No flashcards due for review!', 'success');
            return;
        }

        displayFlashcard();
    } catch (error) {
        showMessage('Error loading flashcards', 'error');
        console.error(error);
    } finally {
        showLoading(false);
    }
}

async function loadAllFlashcards() {
    const level = document.getElementById('flashcard-level').value;
    const topic = document.getElementById('flashcard-topic').value;

    showLoading(true);
    try {
        const params = new URLSearchParams();
        if (level) params.append('level', level);
        if (topic) params.append('topic', topic);

        const response = await fetch(`${API_BASE}/api/flashcards?${params}`);
        const data = await response.json();
        currentFlashcards = data.flashcards;
        currentFlashcardIndex = 0;

        if (currentFlashcards.length === 0) {
            showMessage('No flashcards found for these filters', 'error');
            return;
        }

        displayFlashcard();
    } catch (error) {
        showMessage('Error loading flashcards', 'error');
        console.error(error);
    } finally {
        showLoading(false);
    }
}

function displayFlashcard() {
    if (currentFlashcards.length === 0) return;

    const card = currentFlashcards[currentFlashcardIndex];
    const container = document.getElementById('flashcard-display');

    container.innerHTML = `
        <div class="flashcard" id="current-flashcard" onclick="flipCard()">
            <div class="flashcard-front">
                <div class="flashcard-text">${card.front}</div>
                <div class="flashcard-meta">
                    ${card.level} | ${card.topic} | ${card.difficulty}
                </div>
                <p style="margin-top: 1rem; color: #64748b; font-size: 0.875rem;">Click to flip</p>
            </div>
            <div class="flashcard-back" style="display: none;">
                <div class="flashcard-text">${card.back}</div>
            </div>
        </div>
        <div class="flashcard-actions">
            <button class="quality-btn hard" onclick="rateCard(2)">Hard 😓</button>
            <button class="quality-btn medium" onclick="rateCard(3)">Medium 🤔</button>
            <button class="quality-btn easy" onclick="rateCard(5)">Easy 😊</button>
        </div>
        <p style="text-align: center; margin-top: 1rem; color: #64748b;">
            Card ${currentFlashcardIndex + 1} of ${currentFlashcards.length}
        </p>
    `;
}

function flipCard() {
    const card = document.getElementById('current-flashcard');
    const front = card.querySelector('.flashcard-front');
    const back = card.querySelector('.flashcard-back');

    if (front.style.display !== 'none') {
        front.style.display = 'none';
        back.style.display = 'block';
    } else {
        front.style.display = 'block';
        back.style.display = 'none';
    }
}

async function rateCard(quality) {
    const card = currentFlashcards[currentFlashcardIndex];

    try {
        await fetch(`${API_BASE}/api/flashcards/review`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                flashcard_id: card.id,
                quality: quality
            })
        });

        // Move to next card
        currentFlashcardIndex++;

        if (currentFlashcardIndex < currentFlashcards.length) {
            displayFlashcard();
        } else {
            document.getElementById('flashcard-display').innerHTML = `
                <div class="flashcard-empty">
                    <h3>🎉 Great job!</h3>
                    <p>You've reviewed all cards in this session.</p>
                    <button class="btn btn-primary" onclick="loadDueFlashcards()">
                        Start New Session
                    </button>
                </div>
            `;
        }

        // Refresh stats
        loadFlashcardStats();

    } catch (error) {
        showMessage('Error recording review', 'error');
        console.error(error);
    }
}

// Quiz
async function loadQuizStats() {
    try {
        const stats = await fetch(`${API_BASE}/api/quiz/stats`).then(r => r.json());
        document.getElementById('quiz-total').textContent = stats.total_attempts;
        document.getElementById('quiz-acc').textContent = `${stats.accuracy}%`;
        document.getElementById('quiz-time').textContent = `${stats.average_time}s`;
    } catch (error) {
        console.error('Error loading quiz stats:', error);
    }
}

async function startQuiz() {
    const level = document.getElementById('quiz-level').value;
    const topic = document.getElementById('quiz-topic').value;
    const count = document.getElementById('quiz-count').value;

    showLoading(true);
    try {
        const params = new URLSearchParams({ count });
        if (level) params.append('level', level);
        if (topic) params.append('topic', topic);

        const response = await fetch(`${API_BASE}/api/quiz/random?${params}`);
        const data = await response.json();
        currentQuiz = data.questions;
        currentQuestionIndex = 0;
        quizAnswers = [];
        quizStartTime = Date.now();

        if (currentQuiz.length === 0) {
            showMessage('No questions found for these filters', 'error');
            return;
        }

        // Hide results if showing
        document.getElementById('quiz-results').style.display = 'none';

        displayQuestion();
    } catch (error) {
        showMessage('Error loading quiz', 'error');
        console.error(error);
    } finally {
        showLoading(false);
    }
}

function displayQuestion() {
    if (currentQuiz.length === 0) return;

    const question = currentQuiz[currentQuestionIndex];
    const container = document.getElementById('quiz-display');

    const options = [
        { label: 'A', text: question.option_a },
        { label: 'B', text: question.option_b },
        { label: 'C', text: question.option_c }
    ];

    if (question.option_d) {
        options.push({ label: 'D', text: question.option_d });
    }

    container.innerHTML = `
        <div class="quiz-question">
            <div class="question-header">
                <span>Question ${currentQuestionIndex + 1} of ${currentQuiz.length}</span>
                <span>${question.level} | ${question.topic}</span>
            </div>
            <div class="question-text">${question.question}</div>
            <div class="quiz-options">
                ${options.map(opt => `
                    <div class="quiz-option" onclick="selectAnswer('${opt.label}', ${question.id})">
                        <strong>${opt.label}.</strong> ${opt.text}
                    </div>
                `).join('')}
            </div>
            <div id="question-explanation" style="display: none;"></div>
            <div class="quiz-navigation">
                <button class="btn btn-secondary" onclick="previousQuestion()"
                        ${currentQuestionIndex === 0 ? 'disabled' : ''}>
                    Previous
                </button>
                <button class="btn btn-primary" id="next-btn" onclick="nextQuestion()" disabled>
                    ${currentQuestionIndex === currentQuiz.length - 1 ? 'Finish' : 'Next'}
                </button>
            </div>
        </div>
    `;
}

let selectedAnswer = null;
let questionStartTime = Date.now();

async function selectAnswer(answer, questionId) {
    selectedAnswer = answer;
    questionStartTime = questionStartTime || Date.now();
    const timeTaken = Math.floor((Date.now() - questionStartTime) / 1000);

    // Highlight selected answer
    document.querySelectorAll('.quiz-option').forEach(opt => {
        opt.classList.remove('selected');
    });
    event.target.closest('.quiz-option').classList.add('selected');

    // Submit answer
    showLoading(true);
    try {
        const response = await fetch(`${API_BASE}/api/quiz/submit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question_id: questionId,
                user_answer: answer,
                time_taken: timeTaken
            })
        });

        const result = await response.json();
        quizAnswers.push(result);

        // Show feedback
        document.querySelectorAll('.quiz-option').forEach(opt => {
            const optionLabel = opt.querySelector('strong').textContent.replace('.', '');
            if (optionLabel === result.correct_answer) {
                opt.classList.add('correct');
            } else if (optionLabel === answer && !result.is_correct) {
                opt.classList.add('incorrect');
            }
            opt.onclick = null; // Disable further clicks
        });

        // Show explanation
        const explanationDiv = document.getElementById('question-explanation');
        explanationDiv.style.display = 'block';
        explanationDiv.innerHTML = `
            <div class="quiz-explanation">
                <strong>${result.is_correct ? '✅ Correct!' : '❌ Incorrect'}</strong>
                <p>${result.explanation}</p>
            </div>
        `;

        // Enable next button
        document.getElementById('next-btn').disabled = false;

    } catch (error) {
        showMessage('Error submitting answer', 'error');
        console.error(error);
    } finally {
        showLoading(false);
    }
}

function nextQuestion() {
    currentQuestionIndex++;
    questionStartTime = Date.now();
    selectedAnswer = null;

    if (currentQuestionIndex < currentQuiz.length) {
        displayQuestion();
    } else {
        showQuizResults();
    }
}

function previousQuestion() {
    if (currentQuestionIndex > 0) {
        currentQuestionIndex--;
        displayQuestion();
    }
}

function showQuizResults() {
    const correct = quizAnswers.filter(a => a.is_correct).length;
    const total = quizAnswers.length;
    const percentage = Math.round((correct / total) * 100);

    document.getElementById('quiz-display').style.display = 'none';
    const resultsDiv = document.getElementById('quiz-results');
    resultsDiv.style.display = 'block';

    document.getElementById('results-summary').innerHTML = `
        <div style="text-align: center; padding: 2rem;">
            <h2 style="color: var(--primary-color); font-size: 3rem; margin-bottom: 1rem;">
                ${percentage}%
            </h2>
            <p style="font-size: 1.25rem; margin-bottom: 2rem;">
                You got ${correct} out of ${total} questions correct!
            </p>
            <button class="btn btn-primary" onclick="startQuiz()">Take Another Quiz</button>
        </div>
    `;

    // Refresh stats
    loadQuizStats();
}

// Progress
async function loadProgress() {
    try {
        const [streak, progress] = await Promise.all([
            fetch(`${API_BASE}/api/progress/streak`).then(r => r.json()),
            fetch(`${API_BASE}/api/progress/overall`).then(r => r.json())
        ]);

        document.getElementById('current-streak').textContent = streak.current_streak;
        document.getElementById('longest-streak').textContent = streak.longest_streak;

        const masteryPercentage = Math.round(progress.average_mastery);
        document.querySelector('.progress-percentage').textContent = `${masteryPercentage}%`;

        // Update progress circle
        const circle = document.getElementById('overall-mastery');
        circle.style.background = `conic-gradient(var(--primary-color) ${masteryPercentage}%, var(--border-color) 0%)`;

        // Load level progress (default L1)
        showLevelProgress('L1');

    } catch (error) {
        console.error('Error loading progress:', error);
    }
}

async function showLevelProgress(level) {
    // Update active tab
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    event?.target?.classList.add('active');

    try {
        const response = await fetch(`${API_BASE}/api/progress/level/${level}`);
        const data = await response.json();

        const container = document.getElementById('level-progress-container');

        if (data.progress.length === 0) {
            container.innerHTML = '<p>No progress recorded for this level yet.</p>';
            return;
        }

        container.innerHTML = `
            <div style="display: grid; gap: 1rem;">
                ${data.progress.map(p => `
                    <div style="background: var(--card-bg); padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <h4>${p.topic}</h4>
                        <div style="display: flex; justify-content: space-between; margin-top: 0.5rem;">
                            <span>Quiz Accuracy: <strong>${p.quiz_accuracy.toFixed(1)}%</strong></span>
                            <span>Cards: <strong>${p.cards_mastered}/${p.cards_total}</strong></span>
                            <span>Time: <strong>${p.time_spent} min</strong></span>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;

    } catch (error) {
        console.error('Error loading level progress:', error);
    }
}

// Content Generation
async function generateFlashcards() {
    const level = document.getElementById('gen-level').value;
    const topic = document.getElementById('gen-topic').value;
    const content = document.getElementById('gen-content').value;
    const count = document.getElementById('gen-flashcard-count').value;

    if (!topic || !content) {
        showGenerationStatus('Please fill in all fields', 'error');
        return;
    }

    showLoading(true);
    showGenerationStatus('Generating flashcards with Claude AI...', 'success');

    try {
        const response = await fetch(`${API_BASE}/api/generate/flashcards`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                level,
                topic,
                content,
                flashcard_count: parseInt(count)
            })
        });

        const result = await response.json();

        if (response.ok) {
            showGenerationStatus(`✅ ${result.message}`, 'success');
            loadFlashcardStats();
        } else {
            showGenerationStatus(`❌ Error: ${result.detail}`, 'error');
        }

    } catch (error) {
        showGenerationStatus('❌ Error generating flashcards. Make sure ANTHROPIC_API_KEY is set.', 'error');
        console.error(error);
    } finally {
        showLoading(false);
    }
}

async function generateQuiz() {
    const level = document.getElementById('gen-level').value;
    const topic = document.getElementById('gen-topic').value;
    const content = document.getElementById('gen-content').value;
    const count = document.getElementById('gen-quiz-count').value;

    if (!topic || !content) {
        showGenerationStatus('Please fill in all fields', 'error');
        return;
    }

    showLoading(true);
    showGenerationStatus('Generating quiz questions with Claude AI...', 'success');

    try {
        const response = await fetch(`${API_BASE}/api/generate/quiz`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                level,
                topic,
                content,
                question_count: parseInt(count)
            })
        });

        const result = await response.json();

        if (response.ok) {
            showGenerationStatus(`✅ ${result.message}`, 'success');
            loadQuizStats();
        } else {
            showGenerationStatus(`❌ Error: ${result.detail}`, 'error');
        }

    } catch (error) {
        showGenerationStatus('❌ Error generating quiz. Make sure ANTHROPIC_API_KEY is set.', 'error');
        console.error(error);
    } finally {
        showLoading(false);
    }
}

async function generateBoth() {
    showLoading(true);
    await generateFlashcards();
    await generateQuiz();
    showLoading(false);
}

function showGenerationStatus(message, type) {
    const statusDiv = document.getElementById('generation-status');
    statusDiv.textContent = message;
    statusDiv.className = `status-message ${type}`;
    statusDiv.style.display = 'block';
}

// Topics
async function loadTopics() {
    try {
        const response = await fetch(`${API_BASE}/api/topics`);
        const data = await response.json();

        // Populate flashcard topic dropdown
        const flashcardTopicSelect = document.getElementById('flashcard-topic');
        const quizTopicSelect = document.getElementById('quiz-topic');

        const allTopics = new Set();
        Object.values(data.topics).forEach(topics => {
            topics.forEach(topic => allTopics.add(topic));
        });

        allTopics.forEach(topic => {
            flashcardTopicSelect.innerHTML += `<option value="${topic}">${topic}</option>`;
            quizTopicSelect.innerHTML += `<option value="${topic}">${topic}</option>`;
        });

    } catch (error) {
        console.error('Error loading topics:', error);
    }
}

// Utility functions
function showLoading(show) {
    document.getElementById('loading-overlay').style.display = show ? 'flex' : 'none';
}

function showMessage(message, type) {
    alert(message); // Simple alert for now, can be enhanced with a toast notification
}
