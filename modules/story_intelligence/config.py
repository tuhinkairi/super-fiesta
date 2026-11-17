
from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class StoryIntelligenceSettings(BaseSettings):

    # Our Gemini API key
    gemini_api_key: SecretStr

    # The AI model we'll initially use
    gemini_model: str = "gemini-3.8-flash"

    # Configuration for reading the .env file
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> StoryIntelligenceSettings:
    return StoryIntelligenceSettings()
