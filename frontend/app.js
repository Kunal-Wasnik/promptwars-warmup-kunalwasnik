// State management
let currentSessionId = null;
let currentTopic = "";
let currentDifficulty = "beginner";

// DOM Elements
const screenSetup = document.getElementById('screen-setup');
const screenLearn = document.getElementById('screen-learn');
const setupForm = document.getElementById('setup-form');
const startBtn = document.getElementById('start-btn');
const analyzeBtn = document.getElementById('analyze-btn');
const resetBtn = document.getElementById('reset-btn');

const toggleLoader = (btn, isLoading, loadingText = "Thinking...") => {
    const textSpan = btn.querySelector('.btn-text');
    const loader = btn.querySelector('.loader');
    
    if (isLoading) {
        if (!btn._originalText) btn._originalText = textSpan.textContent;
        textSpan.textContent = loadingText;
        loader.classList.remove('hidden');
        btn.disabled = true;
        btn.classList.add('loading');
    } else {
        textSpan.textContent = btn._originalText || "Submit";
        loader.classList.add('hidden');
        btn.disabled = false;
        btn.classList.remove('loading');
    }
};

const switchScreen = (screenId) => {
    console.log(`Switching to screen: ${screenId}`);
    document.querySelectorAll('.screen').forEach(s => {
        if (s.id === screenId) {
            s.classList.add('active');
            s.classList.remove('hidden');
        } else {
            s.classList.remove('active');
            s.classList.add('hidden');
        }
    });
};

// Flow 1: Start Session
setupForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const topicInput = document.getElementById('topic-input');
    currentTopic = topicInput.value.trim();
    currentDifficulty = document.getElementById('difficulty-select').value;
    
    if (!currentTopic) return;

    console.log(`Starting session for: ${currentTopic}`);
    toggleLoader(startBtn, true, "Architecting Curriculum...");
    
    try {
        const res = await fetch('/api/learn/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic: currentTopic, difficulty: currentDifficulty })
        });
        
        if (!res.ok) {
            const errData = await res.json();
            throw new Error(errData.detail || "Failed to start session");
        }
        
        const data = await res.json();
        console.log("Received Architect data:", data);
        
        currentSessionId = data.session_id;
        
        // Populate Learn Screen
        document.getElementById('active-topic').textContent = data.topic || currentTopic;
        document.getElementById('topic-overview').textContent = data.overview || "No overview available.";
        document.getElementById('suggested-prompt').textContent = data.suggested_prompt || "Explain the concept below:";
        
        const conceptsList = document.getElementById('key-concepts-list');
        conceptsList.innerHTML = "";
        if (data.key_concepts && data.key_concepts.length > 0) {
            data.key_concepts.forEach(concept => {
                const li = document.createElement('li');
                li.textContent = concept;
                conceptsList.appendChild(li);
            });
        } else {
            conceptsList.innerHTML = "<li>General concepts will be covered.</li>";
        }

        // Populate Links
        const resourcesSection = document.getElementById('resources-section');
        const linksList = document.getElementById('links-list');
        linksList.innerHTML = "";
        
        if (data.links && data.links.length > 0) {
            data.links.forEach(link => {
                const li = document.createElement('li');
                const a = document.createElement('a');
                a.href = link.url;
                a.target = "_blank";
                a.rel = "noopener noreferrer";
                a.textContent = link.title;
                li.appendChild(a);
                linksList.appendChild(li);
            });
            resourcesSection.classList.remove('hidden');
        } else {
            resourcesSection.classList.add('hidden');
        }

        // Clear workspace
        document.getElementById('explanation-input').value = "";
        document.getElementById('feedback-panel').classList.add('hidden');
        
        switchScreen('screen-learn');
    } catch (err) {
        console.error("Session Start Error:", err);
        alert(`Error: ${err.message}\n\nPlease try again. The AI might be busy.`);
    } finally {
        toggleLoader(startBtn, false);
    }
});

// Flow 2: Analyze Explanation
analyzeBtn.addEventListener('click', async () => {
    const explanationInput = document.getElementById('explanation-input');
    const explanation = explanationInput.value.trim();
    
    if (explanation.length < 10) {
        alert("Please write a bit more so I can analyze your understanding.");
        return;
    }
    
    console.log("Analyzing explanation...");
    toggleLoader(analyzeBtn, true, "Evaluating Understanding...");
    document.getElementById('feedback-panel').classList.add('hidden');
    
    try {
        const res = await fetch('/api/learn/explain', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                topic: currentTopic,
                explanation: explanation,
                difficulty: currentDifficulty,
                session_id: currentSessionId
            })
        });
        
        if (!res.ok) {
            const errData = await res.json();
            throw new Error(errData.detail || "Analysis failed");
        }
        
        const data = await res.json();
        console.log("Received Analysis data:", data);
        const analysis = data.analysis;
        
        // Populate Feedback
        document.getElementById('score-value').textContent = analysis.mastery_score;
        document.getElementById('feedback-encouragement').textContent = analysis.encouragement;
        
        const renderList = (id, items, fallback) => {
            const el = document.getElementById(id);
            el.innerHTML = "";
            if (items && items.length > 0) {
                items.forEach(text => {
                    const li = document.createElement('li');
                    li.textContent = text;
                    el.appendChild(li);
                });
            } else {
                el.innerHTML = `<li>${fallback}</li>`;
            }
        };

        renderList('feedback-correct', analysis.correct, "Keep trying to capture the key points!");
        renderList('feedback-missing', analysis.missing, "You've covered the essentials!");
            
        document.getElementById('feedback-lesson').textContent = analysis.micro_lesson;
        
        document.getElementById('feedback-panel').classList.remove('hidden');
        
        // Scroll to feedback
        document.getElementById('feedback-panel').scrollIntoView({ behavior: 'smooth' });
        
    } catch (err) {
        console.error("Analysis Error:", err);
        alert(`Error: ${err.message}\n\nPlease check your internet and try again.`);
    } finally {
        toggleLoader(analyzeBtn, false);
    }
});

// Reset
resetBtn.addEventListener('click', () => {
    if (confirm("Start a new topic? Your current session progress will be lost.")) {
        currentSessionId = null;
        document.getElementById('topic-input').value = "";
        switchScreen('screen-setup');
    }
});
