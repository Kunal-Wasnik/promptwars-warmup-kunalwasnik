"""
Pydantic v2 data models for FlowLearn API.
All request/response schemas are defined here as the single source of truth.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class DifficultyLevel(str, Enum):
    """Supported difficulty levels for personalized content adaptation."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


# ── Request Models ──────────────────────────────────────────────────────────

class StartSessionRequest(BaseModel):
    """Request to initialize a new learning session for a topic."""
    topic: str = Field(..., min_length=2, max_length=200, description="The concept to study")
    difficulty: DifficultyLevel = Field(default=DifficultyLevel.BEGINNER, description="User's current level")


class ExplainRequest(BaseModel):
    """Request containing the student's explanation attempt for gap analysis."""
    topic: str = Field(..., min_length=2, max_length=200, description="The concept being explained")
    explanation: str = Field(..., min_length=10, max_length=3000, description="Student's explanation in their own words")
    difficulty: DifficultyLevel = Field(default=DifficultyLevel.BEGINNER)
    session_id: Optional[str] = Field(default=None, description="Session ID for continuity tracking")


class ResourceLink(BaseModel):
    """External educational resource link."""
    title: str
    url: str


# ── Response Models ─────────────────────────────────────────────────────────

class GapAnalysis(BaseModel):
    """Structured analysis of a student's concept explanation."""
    correct: list[str] = Field(description="Concepts the student correctly identified")
    missing: list[str] = Field(description="Important concepts that were missed")
    misconceptions: list[str] = Field(description="Incorrect statements requiring correction")
    micro_lesson: str = Field(description="Targeted micro-lesson covering only the identified gaps")
    mastery_score: int = Field(ge=0, le=100, description="Mastery score from 0 to 100")
    encouragement: str = Field(description="Personalized motivational message")
    next_steps: str = Field(description="Specific recommendation for the student's next study action")


class StartSessionResponse(BaseModel):
    """Response for a new learning session initialization."""
    status: str = "success"
    session_id: str
    topic: str
    overview: str
    key_concepts: list[str]
    suggested_prompt: str
    links: List[ResourceLink] = Field(default_factory=list)


class ExplainResponse(BaseModel):
    """Response containing the AI-powered gap analysis of a student's explanation."""
    status: str = "success"
    topic: str
    analysis: GapAnalysis
    session_id: str


class HealthResponse(BaseModel):
    """API health check response."""
    status: str
    message: str
    version: str
    model: str
    environment: str
