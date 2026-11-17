"""
Configuration for recommendation generation and selection.

Defines validated defaults for scoring, filtering, result limits,
and recommendation diversification.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
import math

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.recommendation.scoring import (
    ScoringWeights,
)


@dataclass(frozen=True, slots=True)
class RecommendationConfig:
    """Validated configuration for the recommendation module."""

    # Result selection
    default_limit: int = 10
    minimum_score: float = 0.0

    # Recommendation diversification
    diversification_enabled: bool = True
    max_per_category: int | None = 3
    max_per_topic: int | None = 3
    max_per_content_format: int | None = 5

    # Recommendation scoring
    scoring_weights: ScoringWeights = field(
        default_factory=ScoringWeights
    )

    def __post_init__(self) -> None:
        """Validate configuration values after initialization."""

        if (
            isinstance(self.default_limit, bool)
            or not isinstance(self.default_limit, int)
            or self.default_limit <= 0
        ):
            raise ValueError(
                "default_limit must be a positive integer."
            )

        if (
            isinstance(self.minimum_score, bool)
            or not isinstance(self.minimum_score, (int, float))
            or not math.isfinite(self.minimum_score)
            or not 0.0 <= self.minimum_score <= 1.0
        ):
            raise ValueError(
                "minimum_score must be a finite number between 0 and 1."
            )

        if not isinstance(self.diversification_enabled, bool):
            raise ValueError(
                "diversification_enabled must be a boolean."
            )

        self._validate_limit(
            "max_per_category",
            self.max_per_category,
        )
        self._validate_limit(
            "max_per_topic",
            self.max_per_topic,
        )
        self._validate_limit(
            "max_per_content_format",
            self.max_per_content_format,
        )

        if not isinstance(self.scoring_weights, ScoringWeights):
            raise TypeError(
                "scoring_weights must be a ScoringWeights instance."
            )

    @staticmethod
    def _validate_limit(
        field_name: str,
        value: int | None,
    ) -> None:
        """Validate an optional positive diversification limit."""

        if value is None:
            return

        if (
            isinstance(value, bool)
            or not isinstance(value, int)
            or value <= 0
        ):
            raise ValueError(
                f"{field_name} must be a positive integer or None."
            )


@lru_cache(maxsize=1)
def get_recommendation_config() -> RecommendationConfig:
    """
    Return the cached default recommendation configuration.

    The returned configuration is immutable and can safely be shared
    across recommendation services.
    """

    return RecommendationConfig()
