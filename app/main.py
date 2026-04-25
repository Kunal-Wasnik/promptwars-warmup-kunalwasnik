"""
FlowLearn — FastAPI Application Entry Point
Personalized Learning Companion powered by Google Gemini 3 AI.
"""
import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

from app.config import settings
from app.routers import learn
from app.models import HealthResponse

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="FlowLearn API",
    description=(
        "An intelligent learning companion that personalizes content using the Feynman Technique "
        "and Google Gemini 3 AI. Helps users learn new concepts by analyzing their explanations "
        "and providing targeted, adaptive micro-lessons."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={"name": "FlowLearn Team", "url": "https://github.com"},
)

# ── Middleware ───────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

# ── Routers ──────────────────────────────────────────────────────────────────
app.include_router(learn.router)

# ── Static Files ─────────────────────────────────────────────────────────────
if os.path.exists(settings.frontend_path):
    app.mount("/static", StaticFiles(directory=settings.frontend_path), name="static")
    logger.info("Frontend mounted from: %s", settings.frontend_path)


# ── Core Routes ──────────────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
async def serve_frontend() -> FileResponse:
    """Serve the FlowLearn frontend application."""
    index_file = os.path.join(settings.frontend_path, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file, media_type="text/html")
    return FileResponse(index_file)


@app.get(
    "/api/health",
    response_model=HealthResponse,
    tags=["system"],
    summary="Health check",
    description="Verify the API is running and correctly configured.",
)
async def health_check() -> HealthResponse:
    """Return the current health and configuration status of the API."""
    return HealthResponse(
        status="ok",
        message="FlowLearn API is online",
        version="1.0.0",
        model=settings.gemini_model,
        environment="development" if settings.debug else "production",
    )


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
