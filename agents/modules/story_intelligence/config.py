
from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from model_config import AGENTS_ROOT, get_model_settings


class StoryIntelligenceSettings(BaseSettings):

    # Our Gemini API key
    gemini_api_key: SecretStr = SecretStr("")

    # The AI model we'll initially use
    gemini_model: str = "gemini-3.5-flash"

    # Configuration for reading the .env file
    model_config = SettingsConfigDict(
        env_file=AGENTS_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> StoryIntelligenceSettings:
    shared = get_model_settings()
    return StoryIntelligenceSettings(
        gemini_api_key=shared.gemini_api_key,
        gemini_model=shared.story_model,
    )
