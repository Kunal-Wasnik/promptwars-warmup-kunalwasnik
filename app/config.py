"""
Application settings — loaded from .env via pydantic-settings.
All secrets MUST be in .env, never hardcoded.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    # App metadata
    app_name: str = "FlowLearn — Personalized Learning Companion"
    debug: bool = False
    frontend_path: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

    # Vertex AI Express Mode (preferred) — set in .env
    # Uses GOOGLE_GENAI_API_KEY + GOOGLE_GENAI_USE_VERTEXAI=TRUE
    google_genai_api_key: str = ""
    google_genai_use_vertexai: str = "TRUE"
    google_genai_location: str = "us-central1"

    # Gemini model to use
    # gemini-3.1-flash-lite-preview is the target; gemini-2.0-flash is the stable fallback
    gemini_model: str = "gemini-2.0-flash"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def is_vertex_ai(self) -> bool:
        return self.google_genai_use_vertexai.upper() == "TRUE"


settings = Settings()
