# FlowLearn — Personalized Learning Companion

![FlowLearn Banner](https://img.shields.io/badge/Status-Hackathon_Ready-success?style=for-the-badge) ![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge) ![FastAPI](https://img.shields.io/badge/FastAPI-0.136-009688?style=for-the-badge) ![Gemini](https://img.shields.io/badge/Gemini_3_Flash-Ready-orange?style=for-the-badge)

## 📌 Problem Statement Alignment
This project directly addresses the Promptwars Challenge: *"Create an intelligent assistant that helps users learn new concepts effectively. The system should personalize content and adapt to user pace and understanding."*

**FlowLearn** moves beyond passive AI summaries. Using the **Feynman Technique**, it forces active recall. The user must explain a concept in their own words. The system uses **Google Gemini 3 Flash** to analyze the explanation, pinpoint exact knowledge gaps, and deliver adaptive, micro-lessons tailored to the user's selected difficulty level.

## ✨ Core Features
1. **Feynman Gap Analysis**: Don't just read—explain it. The AI analyzes your explanation for correct points, missing information, and misconceptions.
2. **Adaptive Difficulty**: Content scales to Beginner, Intermediate, or Advanced levels automatically.
3. **Targeted Micro-Lessons**: Instead of re-reading a whole chapter, get a targeted 3-sentence lesson on exactly what you missed.
4. **Premium UI**: Built with a sleek, glassmorphism design system to reduce cognitive load and provide a focused "Digital Sanctuary."

## 🛠️ Tech Stack & Google Services
- **AI Engine**: Google Gemini 3 Flash (`gemini-3-flash-preview`)
- **Backend**: FastAPI (Async, Pydantic v2)
- **Frontend**: Vanilla JS + CSS (Semantic HTML, Accessible ARIA standards)
- **Typography**: Google Fonts (Manrope, Inter)

## 🚀 Setup & Run
1. Rename `.env.example` to `.env` and add your `GEMINI_API_KEY`.
2. Run the development server:
   ```bash
   ./run.ps1
   ```
   *(Or manually with `uv run uvicorn app.main:app --reload`)*
3. Access the application at `http://localhost:8000`

## 🧪 Testing
We believe in robust code. To run the full test suite (which mocks the Gemini API for reliable CI/CD):
```bash
uv add pytest httpx --dev
uv run pytest
```
