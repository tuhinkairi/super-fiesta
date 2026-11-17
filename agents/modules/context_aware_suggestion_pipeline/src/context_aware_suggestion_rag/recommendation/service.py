"""
Recommendation service.

Coordinates recommendation generation, validation, filtering,
ranking, and diversification.
"""

from __future__ import annotations

from collections.abc import Sequence

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.recommendation.config import (
    RecommendationConfig,
    get_recommendation_config,
)
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.recommendation.diversifier import (
    RecommendationDiversifier,
)
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.recommendation.filters import (
    RecommendationFilter,
)
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.recommendation.generator import (
    RecommendationCandidate,
    RecommendationGenerator,
)
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.recommendation.models import (
    Recommendation,
)
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.recommendation.ranking import (
    RecommendationRanker,
)
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.recommendation.validator import (
    RecommendationValidator,
)


class RecommendationService:
    """Orchestrates the recommendation generation workflow."""

    def __init__(
        self,
        *,
        config: RecommendationConfig | None = None,
        generator: RecommendationGenerator | None = None,
        validator: RecommendationValidator | None = None,
        recommendation_filter: RecommendationFilter | None = None,
        ranker: RecommendationRanker | None = None,
        diversifier: RecommendationDiversifier | None = None,
    ) -> None:
        self.config = config or get_recommendation_config()

        self.generator = (
            generator or RecommendationGenerator()
        )

        self.validator = validator or RecommendationValidator()
        self.recommendation_filter = (
            recommendation_filter or RecommendationFilter()
        )
        self.ranker = ranker or RecommendationRanker()
        self.diversifier = (
            diversifier or RecommendationDiversifier()
        )

    def generate(
        self,
        candidates: Sequence[RecommendationCandidate],
        *,
        limit: int | None = None,
        categories: Sequence[str] | None = None,
        content_formats: Sequence[str] | None = None,
        priorities: Sequence[str] | None = None,
        statuses: Sequence[str] | None = None,
        required_keywords: Sequence[str] | None = None,
        target_audience: str | None = None,
    ) -> list[Recommendation]:
        """
        Generate and select recommendations from candidates.

        Args:
            candidates: Recommendation candidates to process.
            limit: Maximum number of recommendations to return.
            categories: Optional category filter.
            content_formats: Optional content format filter.
            priorities: Optional priority filter.
            statuses: Optional status filter.
            required_keywords: Keywords that must be present.
            target_audience: Exact target audience filter.

        Returns:
            A ranked and optionally diversified recommendation list.
        """

        if limit is None:
            limit = self.config.default_limit

        if (
            isinstance(limit, bool)
            or not isinstance(limit, int)
            or limit <= 0
        ):
            raise ValueError("limit must be a positive integer.")

        # Step 1: Generate recommendations.
        recommendations = self.generator.generate(candidates)

        if not recommendations:
            return []

        # Step 2: Validate generated recommendations.
        self.validator.validate_many(recommendations)

        # Step 3: Filter recommendations.
        filtered = self.recommendation_filter.filter(
            recommendations,
            min_score=self.config.minimum_score,
            categories=categories,
            content_formats=content_formats,
            priorities=priorities,
            statuses=statuses,
            required_keywords=required_keywords,
            target_audience=target_audience,
        )

        if not filtered:
            return []

        # Step 4: Rank recommendations.
        ranked = self.ranker.rank(
            filtered,
            limit=limit,
        )

        # Step 5: Diversify recommendations when enabled.
        if self.config.diversification_enabled:
            ranked = self.diversifier.diversify(
                ranked,
                max_per_category=self.config.max_per_category,
                max_per_topic=self.config.max_per_topic,
                max_per_format=self.config.max_per_content_format,
            )

        return ranked[:limit]

    def validate(
        self,
        recommendations: Sequence[Recommendation],
    ) -> bool:
        """Validate an existing collection of recommendations."""

        self.validator.validate_many(recommendations)
        return True

    def filter(
        self,
        recommendations: Sequence[Recommendation],
        *,
        min_score: float | None = None,
        categories: Sequence[str] | None = None,
        content_formats: Sequence[str] | None = None,
        priorities: Sequence[str] | None = None,
        statuses: Sequence[str] | None = None,
        required_keywords: Sequence[str] | None = None,
        target_audience: str | None = None,
    ) -> list[Recommendation]:
        """Filter an existing recommendation collection."""

        if min_score is None:
            min_score = self.config.minimum_score

        return self.recommendation_filter.filter(
            recommendations,
            min_score=min_score,
            categories=categories,
            content_formats=content_formats,
            priorities=priorities,
            statuses=statuses,
            required_keywords=required_keywords,
            target_audience=target_audience,
        )

    def rank(
        self,
        recommendations: Sequence[Recommendation],
        *,
        limit: int | None = None,
    ) -> list[Recommendation]:
        """Rank an existing recommendation collection."""

        if limit is None:
            limit = self.config.default_limit

        return self.ranker.rank(
            recommendations,
            limit=limit,
        )

    def diversify(
        self,
        recommendations: Sequence[Recommendation],
    ) -> list[Recommendation]:
        """Apply the configured diversification rules."""

        if not self.config.diversification_enabled:
            return list(recommendations)

        return self.diversifier.diversify(
            recommendations,
            max_per_category=self.config.max_per_category,
            max_per_topic=self.config.max_per_topic,
            max_per_format=self.config.max_per_content_format,
        )


def create_recommendation_service(
    config: RecommendationConfig | None = None,
) -> RecommendationService:
    """Create a recommendation service with default components."""

    return RecommendationService(config=config)
