"""
Tests for /api/learn/* endpoints.
Uses mocks to isolate Gemini API calls — tests logic, not the external service.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app
from app.models import GapAnalysis

client = TestClient(app)

# ── Shared Mock Data ─────────────────────────────────────────────────────────

MOCK_ANALYSIS = GapAnalysis(
    correct=["Plants use sunlight as energy source", "CO2 is absorbed from air"],
    missing=["Chloroplast is the site of photosynthesis", "Light-dependent reactions", "Calvin cycle"],
    misconceptions=[],
    micro_lesson=(
        "Great start! You correctly identified the inputs. The key thing you missed: "
        "photosynthesis happens inside the chloroplast. It has two stages — "
        "light-dependent reactions (produce ATP) and the Calvin cycle (produce glucose)."
    ),
    mastery_score=55,
    encouragement="You've got a solid foundation! Let's fill in the details.",
    next_steps="Study the two stages of photosynthesis: light reactions and the Calvin cycle.",
)

MOCK_OVERVIEW = {
    "overview": "Photosynthesis is how plants convert sunlight into chemical energy stored as glucose.",
    "key_concepts": ["Chloroplast", "Light reactions", "Calvin cycle", "Glucose", "Oxygen"],
    "suggested_prompt": "Explain photosynthesis as if you were teaching a friend who missed that class.",
}


# ── Validation Tests ─────────────────────────────────────────────────────────

def test_explain_rejects_short_explanation():
    """Explanations under 10 characters must be rejected with 422."""
    response = client.post("/api/learn/explain", json={
        "topic": "Photosynthesis",
        "explanation": "short",
    })
    assert response.status_code == 422


def test_explain_rejects_missing_topic():
    """Requests without a topic must be rejected with 422."""
    response = client.post("/api/learn/explain", json={
        "explanation": "This is a valid explanation of photosynthesis in detail.",
    })
    assert response.status_code == 422


def test_explain_rejects_empty_topic():
    """Empty topic strings must be rejected with 422."""
    response = client.post("/api/learn/explain", json={
        "topic": "",
        "explanation": "This is a valid explanation of photosynthesis in detail.",
    })
    assert response.status_code == 422


def test_start_session_rejects_missing_topic():
    """Session start without topic must return 422."""
    response = client.post("/api/learn/start", json={})
    assert response.status_code == 422


def test_explain_accepts_valid_difficulty_levels():
    """All valid difficulty levels must be accepted (with mocked AI)."""
    with patch("app.routers.learn.analyze_explanation", new_callable=AsyncMock, return_value=MOCK_ANALYSIS):
        for level in ["beginner", "intermediate", "advanced"]:
            response = client.post("/api/learn/explain", json={
                "topic": "Photosynthesis",
                "explanation": "This is my detailed explanation of photosynthesis.",
                "difficulty": level,
            })
            assert response.status_code == 200, f"Failed for difficulty: {level}"


def test_explain_rejects_invalid_difficulty():
    """Invalid difficulty level must be rejected with 422."""
    response = client.post("/api/learn/explain", json={
        "topic": "Photosynthesis",
        "explanation": "This is my detailed explanation of photosynthesis.",
        "difficulty": "expert",
    })
    assert response.status_code == 422


# ── Success Path Tests ───────────────────────────────────────────────────────

@patch("app.routers.learn.analyze_explanation", new_callable=AsyncMock, return_value=MOCK_ANALYSIS)
def test_explain_success_returns_correct_structure(mock_analyze):
    """Successful explain call must return full structured response."""
    response = client.post("/api/learn/explain", json={
        "topic": "Photosynthesis",
        "explanation": "Photosynthesis is when plants use sunlight to make food from water and CO2.",
        "difficulty": "beginner",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["topic"] == "Photosynthesis"
    assert "analysis" in data
    assert "session_id" in data


@patch("app.routers.learn.analyze_explanation", new_callable=AsyncMock, return_value=MOCK_ANALYSIS)
def test_explain_response_has_mastery_score(mock_analyze):
    """Explain response must contain a valid mastery_score between 0 and 100."""
    response = client.post("/api/learn/explain", json={
        "topic": "Photosynthesis",
        "explanation": "Photosynthesis is when plants use sunlight to make food from water and CO2.",
    })
    data = response.json()
    score = data["analysis"]["mastery_score"]
    assert 0 <= score <= 100


@patch("app.routers.learn.analyze_explanation", new_callable=AsyncMock, return_value=MOCK_ANALYSIS)
def test_explain_response_has_correct_and_missing(mock_analyze):
    """Explain response must include both correct and missing lists."""
    response = client.post("/api/learn/explain", json={
        "topic": "Photosynthesis",
        "explanation": "Photosynthesis is when plants use sunlight to make food.",
    })
    data = response.json()["analysis"]
    assert isinstance(data["correct"], list)
    assert isinstance(data["missing"], list)
    assert isinstance(data["micro_lesson"], str)
    assert len(data["micro_lesson"]) > 0


@patch("app.routers.learn.analyze_explanation", new_callable=AsyncMock, return_value=MOCK_ANALYSIS)
def test_explain_preserves_session_id(mock_analyze):
    """Provided session_id must be returned in the response."""
    test_session = "test-session-abc-123"
    response = client.post("/api/learn/explain", json={
        "topic": "Photosynthesis",
        "explanation": "Photosynthesis is when plants use sunlight to make food.",
        "session_id": test_session,
    })
    data = response.json()
    assert data["session_id"] == test_session


@patch("app.routers.learn.get_topic_overview", new_callable=AsyncMock, return_value=MOCK_OVERVIEW)
def test_start_session_success(mock_overview):
    """Successful session start must return session_id and key concepts."""
    response = client.post("/api/learn/start", json={
        "topic": "Photosynthesis",
        "difficulty": "beginner",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "session_id" in data
    assert "key_concepts" in data
    assert len(data["key_concepts"]) > 0
    assert "suggested_prompt" in data


@patch("app.routers.learn.get_topic_overview", new_callable=AsyncMock, return_value=MOCK_OVERVIEW)
def test_start_session_generates_unique_ids(mock_overview):
    """Each session start must return a unique session_id."""
    ids = set()
    for _ in range(3):
        response = client.post("/api/learn/start", json={"topic": "Gravity"})
        ids.add(response.json()["session_id"])
    assert len(ids) == 3
