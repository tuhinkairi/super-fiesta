
"""
Recommendation ranking utilities.

Ranks recommendations using overall score, priority,
and creation timestamp.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Sequence

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.recommendation.models import Recommendation


class RecommendationRanker:
    """Ranks recommendations using multiple criteria."""

    _PRIORITY_WEIGHTS = {
        "critical": 4,
        "high": 3,
        "medium": 2,
        "low": 1,
    }

    def rank(
        self,
        recommendations: Sequence[Recommendation],
        limit: int | None = None,
    ) -> list[Recommendation]:
        """Return recommendations sorted from highest to lowest rank."""

        if isinstance(recommendations, (str, bytes)):
            raise TypeError(
                "Recommendations must be a sequence of Recommendation objects."
            )

        if not isinstance(recommendations, Sequence):
            raise TypeError("Recommendations must be a sequence.")

        if any(
            not isinstance(item, Recommendation)
            for item in recommendations
        ):
            raise TypeError(
                "Every item must be a Recommendation instance."
            )

        if limit is not None:
            if isinstance(limit, bool) or not isinstance(limit, int):
                raise TypeError("Limit must be an integer or None.")

            if limit <= 0:
                raise ValueError("Limit must be greater than zero.")

        ranked = sorted(
            recommendations,
            key=self._ranking_key,
            reverse=True,
        )

        return ranked[:limit] if limit is not None else ranked

    def _ranking_key(
        self,
        recommendation: Recommendation,
    ) -> tuple[float, int, float]:
        """Generate the ranking key."""

        score = float(recommendation.score.overall)

        priority = self._get_priority_weight(
            recommendation.priority
        )

        timestamp = self._get_timestamp(
            recommendation.created_at
        )

        return score, priority, timestamp

    @classmethod
    def _get_priority_weight(cls, priority: object) -> int:
        """Convert priority into a numeric weight."""

        value = getattr(priority, "value", priority)

        if not isinstance(value, str):
            return 0

        return cls._PRIORITY_WEIGHTS.get(value.lower(), 0)

    @staticmethod
    def _get_timestamp(created_at: object) -> float:
        """Convert datetime into a Unix timestamp."""

        if not isinstance(created_at, datetime):
            return 0.0

        if created_at.tzinfo is None:
            created_at = created_at.replace(
                tzinfo=timezone.utc
            )

        return created_at.timestamp()


def rank_recommendations(
    recommendations: Sequence[Recommendation],
    limit: int | None = None,
) -> list[Recommendation]:
    """Convenience function for ranking recommendations."""

    return RecommendationRanker().rank(
        recommendations=recommendations,
        limit=limit,
    )
