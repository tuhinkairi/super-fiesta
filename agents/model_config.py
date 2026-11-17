"""Shared model settings for the three agent modules."""

from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

AGENTS_ROOT = Path(__file__).resolve().parent
ENV_FILE = AGENTS_ROOT / ".env"
load_dotenv(ENV_FILE, override=False)


class ModelSettings(BaseSettings):
    """Provider credentials and model IDs controlled from agents/.env."""

    gemini_api_key: str = ""
    story_model: str = "gemini-3.5-flash"
    inspiration_model: str = "gemini-3.5-flash"
    suggestion_model: str = "gemini-3.5-flash"
    embedding_model: str = "gemini-embedding-001"

    model_config = SettingsConfigDict(
        env_file=ENV_FILE, env_file_encoding="utf-8", extra="ignore"
    )


@lru_cache(maxsize=1)
def get_model_settings() -> ModelSettings:
    return ModelSettings()
