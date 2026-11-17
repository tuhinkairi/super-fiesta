"""
Standardized data models for external intelligence sources.

These models normalize trend and news information so that
different external providers can be used interchangeably.
"""

from datetime import datetime, timezone
from typing import Any

from pydantic import Field, HttpUrl

from context_aware_suggestion_rag.domain.entities import DomainEntity


def current_utc_time() -> datetime:
    """Return the current UTC timestamp."""
    return datetime.now(timezone.utc)


class IntelligenceModel(DomainEntity):
    """Base model for external intelligence data."""


class TrendData(IntelligenceModel):
    """Represents a trending search topic or keyword."""

    keyword: str = Field(min_length=1, max_length=300)
    value: float = Field(default=0.0, ge=0.0)
    formatted_value: str | None = None

    region: str = Field(default="IN", min_length=2, max_length=10)
    language: str = Field(default="en", min_length=2, max_length=20)

    category: str | None = None
    related_queries: list[str] = Field(default_factory=list)

    source: str = Field(default="google_trends")
    collected_at: datetime = Field(default_factory=current_utc_time)

    metadata: dict[str, Any] = Field(default_factory=dict)


class NewsData(IntelligenceModel):
    """Represents a news article collected from an external source."""

    title: str = Field(min_length=1, max_length=1000)
    description: str = Field(default="", max_length=10000)

    url: HttpUrl
    source_name: str = Field(default="unknown", max_length=300)
    author: str | None = None

    published_at: datetime | None = None
    collected_at: datetime = Field(default_factory=current_utc_time)

    language: str = Field(default="en", min_length=2, max_length=20)
    region: str = Field(default="IN", min_length=2, max_length=10)

    category: str | None = None
    keywords: list[str] = Field(default_factory=list)

    metadata: dict[str, Any] = Field(default_factory=dict)


class IntelligenceCollectionResult(IntelligenceModel):
    """Stores the result of collecting intelligence from a provider."""

    provider: str = Field(min_length=1, max_length=100)
    collection_type: str = Field(min_length=1, max_length=100)

    trends: list[TrendData] = Field(default_factory=list)
    news: list[NewsData] = Field(default_factory=list)

    collected_at: datetime = Field(default_factory=current_utc_time)
    duration_seconds: float = Field(default=0.0, ge=0.0)

    success: bool = True
    warnings: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
