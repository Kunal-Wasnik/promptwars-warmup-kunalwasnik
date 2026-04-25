/**
 * FlowLearn Frontend Logic
 * Implements smooth screen transitions and dynamic card rendering.
 */

const state = {
    currentTopic: '',
    difficulty: 'Beginner'
};

// ── Screen Management ───────────────────────────────────────────────────────
function switchScreen(screenId) {
    document.querySelectorAll('.screen').forEach(s => {
        s.classList.remove('active');
        s.classList.add('hidden');
    });
    const next = document.getElementById(`${screenId}-screen`);
    next.classList.remove('hidden');
    setTimeout(() => next.classList.add('active'), 10);
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ── Event Handlers ───────────────────────────────────────────────────────────
async function startSession() {
    const topic = document.getElementById('topic-input').value.trim();
    if (!topic) return alert('Please enter a topic to start learning.');

    state.currentTopic = topic;
    state.difficulty = document.getElementById('difficulty-select').value;

    switchScreen('loading');
    document.getElementById('loading-text').textContent = `Architecting your curriculum for ${topic}...`;

    try {
        const response = await fetch('/api/learn/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic, difficulty: state.difficulty })
        });
        
        if (!response.ok) throw new Error('Backend failed to architect curriculum');
        const data = await response.json();

        // Update UI
        document.querySelectorAll('.topic-name').forEach(el => el.textContent = data.topic);
        document.getElementById('overview-text').textContent = data.overview;
        document.getElementById('feynman-prompt').textContent = data.suggested_prompt;

        renderConcepts(data.key_concepts);
        renderLinks(data.links);

        switchScreen('learn');
    } catch (err) {
        console.error(err);
        alert('Failed to start session. Please check your connection.');
        switchScreen('setup');
    }
}

async function submitExplanation() {
    const explanation = document.getElementById('explanation-input').value.trim();
    if (!explanation) return alert('Please write an explanation first.');

    switchScreen('loading');
    document.getElementById('loading-text').textContent = `Evaluating your mastery of ${state.currentTopic}...`;

    try {
        const response = await fetch('/api/learn/explain', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                topic: state.currentTopic,
                explanation: explanation,
                difficulty: state.difficulty
            })
        });

        if (!response.ok) throw new Error('Evaluation failed');
        const data = await response.json();

        renderFeedback(data);
        switchScreen('feedback');
    } catch (err) {
        console.error(err);
        alert('Failed to evaluate explanation.');
        switchScreen('learn');
    }
}

// ── Rendering Helpers ────────────────────────────────────────────────────────
function renderConcepts(concepts) {
    const container = document.getElementById('concepts-grid');
    container.innerHTML = '';
    concepts.forEach(concept => {
        const card = document.createElement('div');
        card.className = 'mini-card fade-in';
        card.innerHTML = `
            <h3>${concept}</h3>
            <p>A core pillar of ${state.currentTopic} that we will master together.</p>
        `;
        container.appendChild(card);
    });
}

function renderLinks(links) {
    const container = document.getElementById('links-list');
    container.innerHTML = '';
    if (!links || links.length === 0) {
        container.innerHTML = '<p class="subtitle">No extra resources found for this specific topic.</p>';
        return;
    }
    links.forEach(link => {
        const a = document.createElement('a');
        a.href = link.url;
        a.target = '_blank';
        a.className = 'resource-link fade-in';
        a.innerHTML = `
            <span>${link.title}</span>
            <i class="fas fa-external-link-alt"></i>
        `;
        container.appendChild(a);
    });
}

function renderFeedback(data) {
    document.getElementById('mastery-value').textContent = `${data.mastery_score}%`;
    
    const lessonContainer = document.getElementById('lesson-body');
    // Basic Markdown conversion for bold and lists
    let html = data.micro_lesson
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/### (.*?)\n/g, '<h4>$1</h4>')
        .replace(/\* (.*?)\n/g, '<li>$1</li>');
    
    lessonContainer.innerHTML = html;
    document.getElementById('next-step-text').textContent = data.next_steps;
}

function resetApp() {
    document.getElementById('topic-input').value = '';
    document.getElementById('explanation-input').value = '';
    switchScreen('setup');
}

// Init
document.addEventListener('DOMContentLoaded', () => {
    // Initial state is Setup
});
