"""
Learning router — handles all /api/learn/* endpoints.
Thin route handlers that delegate business logic to the Gemini service.
"""
import uuid
import logging
import httpx
from fastapi import APIRouter, HTTPException
from app.models import (
    ExplainRequest,
    ExplainResponse,
    StartSessionRequest,
    StartSessionResponse,
)
from app.services.gemini import analyze_explanation, get_topic_overview

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/learn", tags=["learning"])


@router.post(
    "/start",
    response_model=StartSessionResponse,
    summary="Start a learning session",
    description="Initialize a personalized learning session. Returns topic overview, key concepts, and a prompt for the student.",
)
async def start_session(request: StartSessionRequest) -> StartSessionResponse:
    """
    Initialize a new learning session for a given topic.

    Calls Gemini AI to generate:
    - A contextual topic overview
    - Key concepts the student should understand
    - A personalized prompt to begin their explanation attempt
    """
    try:
        import time
        start_time = time.time()
        logger.info("Starting session for topic: %s", request.topic)
        overview_data = await get_topic_overview(request.topic, request.difficulty.value)
        duration = time.time() - start_time
        logger.info("Architect finished in %.2fs", duration)
        
        session_id = str(uuid.uuid4())

        return StartSessionResponse(
            session_id=session_id,
            topic=request.topic,
            overview=overview_data["overview"],
            key_concepts=overview_data["key_concepts"],
            suggested_prompt=overview_data["suggested_prompt"],
        )
    except httpx.HTTPStatusError as exc:
        detail = "AI service error. Please check your API key and quota."
        if exc.response.status_code == 429:
            detail = "Rate limit reached. Please wait 60 seconds."
        elif exc.response.status_code == 401:
            detail = "Invalid API Key. Check your .env file."
        
        logger.error("Gemini API error: %s", exc.response.text)
        raise HTTPException(status_code=exc.response.status_code, detail=detail)
    except Exception as exc:
        logger.exception("Unexpected error")
        raise HTTPException(status_code=500, detail=str(exc))



@router.post(
    "/explain",
    response_model=ExplainResponse,
    summary="Analyze a student's explanation",
    description="Uses the Feynman Technique to analyze a student's explanation. Returns gap analysis, mastery score, and a personalized micro-lesson.",
)
async def analyze_student_explanation(request: ExplainRequest) -> ExplainResponse:
    """
    Analyze a student's explanation of a concept using Gemini AI.

    Implements the Feynman Technique:
    1. Identifies what the student got correct
    2. Detects gaps and misconceptions
    3. Generates a targeted micro-lesson covering ONLY the gaps
    4. Assigns a mastery score from 0–100
    5. Provides personalized next-step recommendations
    """
    try:
        import time
        start_time = time.time()
        logger.info("Analyzing explanation for topic: %s", request.topic)
        analysis = await analyze_explanation(
            topic=request.topic,
            explanation=request.explanation,
            difficulty=request.difficulty.value,
        )
        duration = time.time() - start_time
        logger.info("Feynman pipeline finished in %.2fs", duration)
        
        session_id = request.session_id or str(uuid.uuid4())

        return ExplainResponse(
            topic=request.topic,
            analysis=analysis,
            session_id=session_id,
        )
    except httpx.HTTPStatusError as exc:
        detail = "AI service error. Please check your API key and quota."
        if exc.response.status_code == 429:
            detail = "Rate limit reached. Please wait 60 seconds."
        elif exc.response.status_code == 401:
            detail = "Invalid API Key. Check your .env file."
        
        logger.error("Gemini API error: %s", exc.response.text)
        raise HTTPException(status_code=exc.response.status_code, detail=detail)
    except Exception as exc:
        logger.exception("Unexpected error")
        raise HTTPException(status_code=500, detail=str(exc))

