# Functional Specification — FlowLearn

## 1. Executive Summary
- **Problem**: Passive learning (reading AI summaries or watching videos) creates the "illusion of competence." Students think they know a topic but fail when tested.
- **Solution**: FlowLearn is an AI-native active recall engine. It uses the Feynman Technique—forcing the student to explain the concept in their own words.
- **Winning Narrative**: It solves the "Personalized Learning" challenge perfectly. Instead of the AI doing the work *for* the student, the AI acts as a rigorous tutor that proves the student actually learned it.

## 2. Core Features (The "Atomic" Flow)
1. **Topic Initialization**: Student enters a topic and difficulty level. AI generates an overview and a prompt.
2. **Active Recall**: Student types their explanation of the concept.
3. **Surgical Gap Analysis**: Gemini analyzes the text, identifying exact missing pieces and misconceptions.
4. **Targeted Remediation**: Student receives a precise micro-lesson addressing only their gaps, alongside a Mastery Score.

## 3. Tech Stack & Specs
- **Backend**: FastAPI (Python 3.12, Async)
- **AI Service**: Google Gemini 3 Flash (`gemini-3-flash-preview`)
- **Environment**: `uv` (Project Mode)
- **Frontend**: Vanilla JS / CSS (Aether Flow Glassmorphism UI)
- **Testing**: `pytest` with `unittest.mock`

## 4. User Journey
- Step 1: User lands on **Topic Selection** screen. Enters "Photosynthesis" at "Beginner" level.
- Step 2: System generates a context card and prompts: "Explain photosynthesis as if teaching a friend."
- Step 3: User explains it.
- Step 4: AI processes the explanation, returns a Dashboard showing:
  - ✅ Correct Points
  - ⚠️ Missing Context (e.g., "You missed the chloroplasts")
  - 📚 Micro-lesson targeting that gap
  - 💯 Mastery Score

---

## 📅 Roadmap Status
- [x] Spec & Data Models (Completed)
- [x] Backend Happy Path & Error Handling (Completed)
- [x] Test Suite for Automated Assessment (Completed)
- [x] Frontend Premium UI & Accessibility (Completed)
- [x] Integration & Polish (Completed)
