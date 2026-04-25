"""
Tests for core API health and system endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check_returns_ok():
    """Health endpoint must return 200 with status ok."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_health_check_includes_model():
    """Health response must include the active Gemini model name."""
    response = client.get("/api/health")
    data = response.json()
    assert "model" in data
    assert "gemini" in data["model"].lower()


def test_health_check_includes_version():
    """Health response must include the API version string."""
    response = client.get("/api/health")
    data = response.json()
    assert "version" in data
    assert data["version"] == "1.0.0"


def test_root_responds():
    """Root path must respond (serves frontend or 404 gracefully)."""
    response = client.get("/")
    assert response.status_code in (200, 404)


def test_docs_accessible():
    """OpenAPI docs must be accessible for platform assessment."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_schema_accessible():
    """OpenAPI JSON schema must be accessible."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "paths" in schema
