"""
Recommendation selection utilities.

Combines validation, filtering, and ranking to select the most
suitable recommendations from a collection.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.recommendation.filters import (
    RecommendationFilter,
)
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.recommendation.models import (
    Recommendation,
)
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.recommendation.ranking import (
    RecommendationRanker,
)
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.recommendation.validator import (
    RecommendationValidator,
)


class RecommendationSelector:
    """Selects the best recommendations using configurable criteria."""

    def __init__(
        self,
        *,
        validator: RecommendationValidator | None = None,
        recommendation_filter: RecommendationFilter | None = None,
        ranker: RecommendationRanker | None = None,
    ) -> None:
        self.validator = validator or RecommendationValidator()
        self.recommendation_filter = (
            recommendation_filter or RecommendationFilter()
        )
        self.ranker = ranker or RecommendationRanker()

    def select(
        self,
        recommendations: Sequence[Recommendation],
        *,
        limit: int = 10,
        min_score: float | None = None,
        categories: Iterable[str] | None = None,
        content_formats: Iterable[str] | None = None,
        priorities: Iterable[str] | None = None,
        statuses: Iterable[str] | None = None,
        required_keywords: Iterable[str] | None = None,
        target_audience: str | None = None,
    ) -> list[Recommendation]:
        """
        Validate, filter, rank, and select recommendations.

        Args:
            recommendations: Input recommendation collection.
            limit: Maximum number of recommendations to return.
            min_score: Minimum overall recommendation score.
            categories: Allowed recommendation categories.
            content_formats: Allowed content formats.
            priorities: Allowed recommendation priorities.
            statuses: Allowed recommendation statuses.
            required_keywords: Keywords that must all be present.
            target_audience: Required target audience.

        Returns:
            A ranked list containing at most `limit` recommendations.
        """

        if isinstance(limit, bool) or not isinstance(limit, int):
            raise TypeError("limit must be an integer.")

        if limit <= 0:
            raise ValueError("limit must be greater than zero.")

        # Validate the original collection.
        self.validator.validate_many(recommendations)

        # Apply recommendation filters.
        filtered = self.recommendation_filter.filter(
            recommendations,
            min_score=min_score,
            categories=categories,
            content_formats=content_formats,
            priorities=priorities,
            statuses=statuses,
            required_keywords=required_keywords,
            target_audience=target_audience,
        )

        # Rank the filtered recommendations.
        ranked = self.ranker.rank(filtered)

        # Return only the requested number.
        return ranked[:limit]


def select_recommendations(
    recommendations: Sequence[Recommendation],
    *,
    limit: int = 10,
    min_score: float | None = None,
    categories: Iterable[str] | None = None,
    content_formats: Iterable[str] | None = None,
    priorities: Iterable[str] | None = None,
    statuses: Iterable[str] | None = None,
    required_keywords: Iterable[str] | None = None,
    target_audience: str | None = None,
) -> list[Recommendation]:
    """Convenience function for selecting recommendations."""

    return RecommendationSelector().select(
        recommendations,
        limit=limit,
        min_score=min_score,
        categories=categories,
        content_formats=content_formats,
        priorities=priorities,
        statuses=statuses,
        required_keywords=required_keywords,
        target_audience=target_audience,
    )
