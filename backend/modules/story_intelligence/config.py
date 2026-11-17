
from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class StoryIntelligenceSettings(BaseSettings):

    # Our Gemini API key
    gemini_api_key: SecretStr = Field(validation_alias="GEMINI_API_KEY")

    # The AI model we'll initially use
    gemini_model: str = Field(
        default="gemini-3.8-flash", validation_alias="STORY_MODEL"
    )

    embedding_model: str = Field(
        default="gemini-embedding-001", validation_alias="EMBEDDING_MODEL"
    )

    # Bound provider request time so API worker threads cannot hang indefinitely.
    gemini_timeout_ms: int = Field(default=45_000, gt=0)

    # Configuration for reading the .env file
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[3] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> StoryIntelligenceSettings:
    return StoryIntelligenceSettings()
