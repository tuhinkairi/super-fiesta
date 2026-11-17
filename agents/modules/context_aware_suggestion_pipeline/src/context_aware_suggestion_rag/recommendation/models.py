"""
Data models for the recommendation package.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
import math


def current_utc_time() -> datetime:
    """Return the current timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


class RecommendationStatus(str, Enum):
    """Lifecycle status of a recommendation."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    GENERATED = "generated"
    ARCHIVED = "archived"


class RecommendationCategory(str, Enum):
    """Broad categories of content recommendations."""

    EDUCATIONAL = "educational"
    INFORMATIVE = "informative"
    ENTERTAINMENT = "entertainment"
    NEWS = "news"
    TUTORIAL = "tutorial"
    ANALYSIS = "analysis"
    OPINION = "opinion"
    RESEARCH = "research"
    GENERAL = "general"


@dataclass(slots=True)
class RecommendationScore:
    """Individual scoring dimensions for a recommendation."""

    relevance: float = 0.0
    freshness: float = 0.0
    popularity: float = 0.0
    engagement_potential: float = 0.0
    source_quality: float = 0.0
    overall: float = 0.0

    def __post_init__(self) -> None:
        """Validate all scoring dimensions."""
        fields = (
            "relevance",
            "freshness",
            "popularity",
            "engagement_potential",
            "source_quality",
            "overall",
        )

        for field_name in fields:
            value = getattr(self, field_name)

            if (
                not isinstance(value, (int, float))
                or isinstance(value, bool)
                or not math.isfinite(value)
            ):
                raise ValueError(
                    f"{field_name} must be a finite number."
                )

            if not 0.0 <= value <= 1.0:
                raise ValueError(
                    f"{field_name} must be between 0 and 1."
                )


@dataclass(slots=True)
class Recommendation:
    """A suggested piece of content for a target audience."""

    id: str
    title: str
    description: str
    rationale: str

    category: RecommendationCategory = RecommendationCategory.GENERAL
    content_format: str = "article"

    target_audience: str = "general"
    keywords: list[str] = field(default_factory=list)
    topics: list[str] = field(default_factory=list)

    source_ids: list[str] = field(default_factory=list)
    source_types: list[str] = field(default_factory=list)

    score: RecommendationScore = field(
        default_factory=RecommendationScore
    )

    status: RecommendationStatus = RecommendationStatus.PENDING
    priority: str = "medium"

    created_at: datetime = field(default_factory=current_utc_time)
    updated_at: datetime = field(default_factory=current_utc_time)

    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate recommendation fields."""
        for field_name in ("id", "title", "description", "rationale"):
            value = getattr(self, field_name)

            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"{field_name} must be a non-empty string."
                )

            setattr(self, field_name, value.strip())

        if not isinstance(self.category, RecommendationCategory):
            self.category = RecommendationCategory(self.category)

        if not isinstance(self.status, RecommendationStatus):
            self.status = RecommendationStatus(self.status)

        if not isinstance(self.score, RecommendationScore):
            raise TypeError(
                "score must be a RecommendationScore instance."
            )

        if not isinstance(self.content_format, str) or not self.content_format.strip():
            raise ValueError("content_format cannot be empty.")

        self.content_format = self.content_format.strip().lower()

        if not isinstance(self.priority, str) or not self.priority.strip():
            raise ValueError("priority cannot be empty.")

        self.priority = self.priority.strip().lower()

        if not isinstance(self.target_audience, str) or not self.target_audience.strip():
            raise ValueError("target_audience cannot be empty.")

        self.target_audience = self.target_audience.strip()

        for field_name in (
            "keywords",
            "topics",
            "source_ids",
            "source_types",
        ):
            values = getattr(self, field_name)

            if not isinstance(values, list):
                raise TypeError(f"{field_name} must be a list.")

            if any(
                not isinstance(value, str) or not value.strip()
                for value in values
            ):
                raise ValueError(
                    f"Every value in {field_name} must be non-empty text."
                )

            setattr(
                self,
                field_name,
                [value.strip() for value in values],
            )

        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary.")

        if not isinstance(self.created_at, datetime):
            raise TypeError("created_at must be a datetime.")

        if not isinstance(self.updated_at, datetime):
            raise TypeError("updated_at must be a datetime.")


@dataclass(slots=True)
class RecommendationCollection:
    """A collection of recommendations produced in one operation."""

    recommendations: list[Recommendation] = field(default_factory=list)

    query: str = ""
    total_generated: int = 0

    created_at: datetime = field(default_factory=current_utc_time)

    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate collection data."""
        if not isinstance(self.recommendations, list):
            raise TypeError("recommendations must be a list.")

        if not all(
            isinstance(item, Recommendation)
            for item in self.recommendations
        ):
            raise TypeError(
                "All collection items must be Recommendation objects."
            )

        if not isinstance(self.total_generated, int) or isinstance(
            self.total_generated, bool
        ):
            raise TypeError("total_generated must be an integer.")

        if self.total_generated < 0:
            raise ValueError("total_generated cannot be negative.")

        if self.total_generated == 0:
            self.total_generated = len(self.recommendations)

        if self.total_generated < len(self.recommendations):
            raise ValueError(
                "total_generated cannot be smaller than collection size."
            )

        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary.")

        if not isinstance(self.warnings, list):
            raise TypeError("warnings must be a list.")


@dataclass(slots=True)
class RecommendationEvaluation:
    """Evaluation result for a generated recommendation."""

    recommendation_id: str

    is_relevant: bool
    is_actionable: bool
    has_sufficient_sources: bool
    has_clear_title: bool

    quality_score: float = 0.0
    feedback: str = ""

    evaluated_at: datetime = field(default_factory=current_utc_time)

    def __post_init__(self) -> None:
        """Validate evaluation data."""
        if not isinstance(self.recommendation_id, str) or not self.recommendation_id.strip():
            raise ValueError("recommendation_id cannot be empty.")

        self.recommendation_id = self.recommendation_id.strip()

        for field_name in (
            "is_relevant",
            "is_actionable",
            "has_sufficient_sources",
            "has_clear_title",
        ):
            if not isinstance(getattr(self, field_name), bool):
                raise TypeError(f"{field_name} must be a boolean.")

        if (
            not isinstance(self.quality_score, (int, float))
            or isinstance(self.quality_score, bool)
            or not math.isfinite(self.quality_score)
            or not 0.0 <= self.quality_score <= 1.0
        ):
            raise ValueError(
                "quality_score must be between 0 and 1."
            )

        if not isinstance(self.feedback, str):
            raise TypeError("feedback must be a string.")
