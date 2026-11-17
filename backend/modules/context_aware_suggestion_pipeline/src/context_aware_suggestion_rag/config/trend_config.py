"""
Trend and news intelligence configuration.

Controls external trend and news collection, including geographic
targeting, freshness windows, request limits, and provider settings.
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_ENV = Path(__file__).resolve().parents[6] / ".env"


class TrendConfig(BaseSettings):
    """Settings for trend and news intelligence collection."""

    # ---------------------------------------------------------
    # Google Trends configuration
    # ---------------------------------------------------------

    trends_enabled: bool = True

    trends_provider: Literal["google_trends"] = "google_trends"

    trends_region: str = "IN"

    trends_language: str = "en-US"

    trends_timeframe: str = "now 7-d"

    trends_category: int = Field(default=0, ge=0)

    trends_max_results: int = Field(default=20, ge=1, le=100)

    trends_refresh_interval_seconds: int = Field(
        default=3600,
        ge=60,
    )

    trends_request_timeout_seconds: int = Field(
        default=30,
        ge=1,
    )

    trends_max_retries: int = Field(default=3, ge=0)

    trends_min_request_interval_seconds: float = Field(
        default=2.0,
        ge=0,
    )

    # ---------------------------------------------------------
    # News collection configuration
    # ---------------------------------------------------------

    news_enabled: bool = True

    news_provider: Literal["rss"] = "rss"

    news_rss_feeds: list[AnyHttpUrl] = Field(default_factory=list)

    news_max_items: int = Field(
        default=30,
        ge=1,
        le=200,
    )

    news_lookback_hours: int = Field(
        default=72,
        ge=1,
        le=720,
    )

    news_refresh_interval_seconds: int = Field(
        default=1800,
        ge=60,
    )

    news_request_timeout_seconds: int = Field(
        default=20,
        ge=1,
    )

    news_max_retries: int = Field(default=3, ge=0)

    news_min_request_interval_seconds: float = Field(
        default=1.0,
        ge=0,
    )

    news_user_agent: str = "ContextAwareSuggestionRAG/0.1"

    # ---------------------------------------------------------
    # Pydantic settings configuration
    # ---------------------------------------------------------

    model_config = SettingsConfigDict(
        env_file=ROOT_ENV,
        env_file_encoding="utf-8",
        env_prefix="CASR_TREND_",
        case_sensitive=False,
        extra="ignore",
        validate_default=True,
    )


@lru_cache(maxsize=1)
def get_trend_config() -> TrendConfig:
    """Return the cached trend and news configuration."""

    return TrendConfig()


__all__ = [
    "TrendConfig",
    "get_trend_config",
]
