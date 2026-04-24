# AGENT.md — Hackathon Architect

## Project Overview
A FastAPI + Vanilla JS MVP for Promptwars Pune. Prioritizes speed, isolated environments, and premium UI.

## Build & Run Commands
- **Backend**: `./run.ps1`
- **Frontend**: Serves `frontend/index.html` via the backend or a simple live server.
- **Dependencies**: Managed via `uv` (pyproject.toml).

## Coding Standards
- **Python**: Use `async def` for all FastAPI routes. Strict Pydantic v2 validation.
- **Frontend**: Vanilla JS + CSS. No external frameworks unless requested.
- **Visuals**: MUST follow `DESIGN.md` (Glassmorphism, Slate/Sky Blue palette).

## Source of Truth
- **Contracts**: Refer to `artifacts/api_contract.md` before changing any API logic.
- **Specs**: Refer to `artifacts/spec.md` for functional requirements.
- **Logging**: Automatically update `artifacts/PROMPTS.md` after major feature completions.
