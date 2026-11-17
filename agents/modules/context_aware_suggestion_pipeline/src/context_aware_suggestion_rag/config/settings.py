"""
Central application settings.

Uses Pydantic Settings to load and validate configuration
from environment variables and .env files.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    General configuration for the Context-Aware Suggestion RAG package.

    Provider-specific settings are maintained separately.
    """

    # --------------------------------------------------------
    # Application
    # --------------------------------------------------------

    app_name: str = "Context-Aware Suggestion RAG"

    environment: Literal[
        "development",
        "testing",
        "production",
    ] = "development"

    debug: bool = False

    log_level: Literal[
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ] = "INFO"

    # --------------------------------------------------------
    # Default Content Preferences
    # --------------------------------------------------------

    default_language: str = "en"

    default_region: str = "IN"

    # --------------------------------------------------------
    # Time Configuration
    # --------------------------------------------------------

    timezone: str = "Asia/Kolkata"

    # --------------------------------------------------------
    # Document Processing
    # --------------------------------------------------------

    max_document_size_mb: int = Field(
        default=20,
        ge=1,
        le=500,
    )

    # --------------------------------------------------------
    # Cache Configuration
    # --------------------------------------------------------

    cache_enabled: bool = True

    cache_ttl_seconds: int = Field(
        default=3600,
        ge=0,
    )

    # --------------------------------------------------------
    # Environment Configuration
    # --------------------------------------------------------

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="CASR_",
        case_sensitive=False,
        extra="ignore",
        validate_default=True,
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return a cached application settings instance.

    Settings are loaded once and reused throughout the package.
    """

    return Settings()


__all__ = [
    "Settings",
    "get_settings",
]
