# Antigravity Hackathon Mode: FastAPI MVP

> ⚠️ **CRITICAL — Gemini Model Versions (verified live, April 2026)**
> - `gemini-1.5-*` → **DECOMMISSIONED**. Never use.
> - `gemini-2.0-flash` → Stable, widely available.
> - `gemini-2.5-flash` / `gemini-2.5-pro` → Latest 2.x stable.
> - `gemini-3-flash-preview` → Latest Gemini 3 (FREE TIER ✅ — use this as default)
> - `gemini-3-pro-preview` → Gemini 3 Pro (heavier, use for complex reasoning only)
> - `gemini-3.1-flash-lite-preview` → Lightest/fastest Gemini 3 (best for free tier)
> - **DEFAULT for hackathon**: `gemini-3-flash-preview` (fast + latest + free tier friendly)

## 1. Core Directives
- **Speed over Perfection**: Do not spend time on perfect variable naming or complex abstractions. Focus on working code.
- **Vibe Coding Focus**: Leverage Antigravity to bridge the gap between intent and code. Show, don't just tell, how AI built the solution.
- **Async First**: Always use `async def` for routes and use asynchronous database drivers/libraries.
- **Thin Routes**: Move database logic to a `crud.py` or `services.py`. This makes the code easier to debug.
- **No Over-Engineering**: Stick to simple Pydantic schemas and flat folder structures.

## 2. Frontend Guidelines
- **Modern & Premium**: Use HSL colors, glassmorphism, and smooth transitions by default.
- **Vanilla Power**: Unless the USER asks for a framework, use Vanilla JS + CSS to avoid setup overhead.
- **Fast Prototyping**: Use the `generate_image` tool for UI mockups and design inspiration.

## 3. Tooling & Workflow
- **Swagger UI is your UI**: Test backend logic at `/docs` before touching the frontend.
- **Fast Feedback**: Run the dev server with `--reload`.
- **Environment**: Use a `.env` file for all secrets and configs.

## 4. Judging Focus
- **Feature Completeness**: Ensure the "Happy Path" is flawless.
- **UI/UX Polish**: A high-end look can win a hackathon. Prioritize premium styling for the main user flow.
- **Storytelling & Narrative**: Promptwars winners win with a story. We must document the "Prompt Strategy" and the problem-solving journey.
- **Innovation & Viability**: The project must solve a real-world problem in a novel way that feels scalable.
