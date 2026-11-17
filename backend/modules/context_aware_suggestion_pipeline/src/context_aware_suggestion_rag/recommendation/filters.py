
"""
Recommendation filtering utilities.

Provides reusable filtering operations for recommendation collections.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.recommendation.models import (
    Recommendation,
)


class RecommendationFilter:
    """Filters recommendations using configurable criteria."""

    def filter(
        self,
        recommendations: Sequence[Recommendation],
        *,
        min_score: float | None = None,
        categories: Iterable[str] | None = None,
        content_formats: Iterable[str] | None = None,
        priorities: Iterable[str] | None = None,
        statuses: Iterable[str] | None = None,
        required_keywords: Iterable[str] | None = None,
        target_audience: str | None = None,
    ) -> list[Recommendation]:
        """
        Filter recommendations.

        All supplied criteria are combined using AND logic.
        Values within the same criterion use OR logic.
        Required keywords use AND logic.
        """

        self._validate_recommendations(recommendations)

        # Validate minimum score.
        if min_score is not None:
            if isinstance(min_score, bool) or not isinstance(
                min_score, (int, float)
            ):
                raise TypeError("min_score must be numeric.")

            if not 0.0 <= min_score <= 1.0:
                raise ValueError(
                    "min_score must be between 0 and 1."
                )

        # Normalize filter criteria.
        category_set = self._normalize_values(categories)
        format_set = self._normalize_values(content_formats)
        priority_set = self._normalize_values(priorities)
        status_set = self._normalize_values(statuses)
        keyword_set = self._normalize_values(required_keywords)

        # Normalize target audience.
        audience = None

        if target_audience is not None:
            if not isinstance(target_audience, str):
                raise TypeError(
                    "target_audience must be a string."
                )

            audience = target_audience.strip().casefold()

            if not audience:
                raise ValueError(
                    "target_audience cannot be empty."
                )

        filtered: list[Recommendation] = []

        for recommendation in recommendations:

            # Minimum score filter.
            if min_score is not None:
                if recommendation.score.overall < min_score:
                    continue

            # Category filter.
            if category_set:
                category = self._enum_value(
                    recommendation.category
                )

                if category not in category_set:
                    continue

            # Content format filter.
            if format_set:
                content_format = self._enum_value(
                    recommendation.content_format
                )

                if content_format not in format_set:
                    continue

            # Priority filter.
            if priority_set:
                priority = self._enum_value(
                    recommendation.priority
                )

                if priority not in priority_set:
                    continue

            # Status filter.
            if status_set:
                status = self._enum_value(
                    recommendation.status
                )

                if status not in status_set:
                    continue

            # Required keywords filter.
            if keyword_set:
                recommendation_keywords = {
                    str(keyword).strip().casefold()
                    for keyword in recommendation.keywords
                }

                if not keyword_set.issubset(
                    recommendation_keywords
                ):
                    continue

            # Target audience filter.
            if audience is not None:
                recommendation_audience = (
                    recommendation.target_audience.strip().casefold()
                )

                if audience != recommendation_audience:
                    continue

            filtered.append(recommendation)

        return filtered

    @staticmethod
    def _validate_recommendations(
        recommendations: Sequence[Recommendation],
    ) -> None:
        """Validate the recommendation collection."""

        if isinstance(recommendations, (str, bytes)):
            raise TypeError(
                "Expected a sequence of recommendations."
            )

        if not isinstance(recommendations, Sequence):
            raise TypeError(
                "Expected a sequence of recommendations."
            )

        if any(
            not isinstance(item, Recommendation)
            for item in recommendations
        ):
            raise TypeError(
                "Every item must be a Recommendation instance."
            )

    @staticmethod
    def _normalize_values(
        values: Iterable[str] | None,
    ) -> set[str]:
        """Normalize iterable filter values."""

        if values is None:
            return set()

        if isinstance(values, str):
            values = [values]

        normalized: set[str] = set()

        for value in values:
            if not isinstance(value, str):
                raise TypeError(
                    "Filter values must be strings."
                )

            value = value.strip().casefold()

            if not value:
                raise ValueError(
                    "Filter values cannot be empty."
                )

            normalized.add(value)

        return normalized

    @staticmethod
    def _enum_value(value: object) -> str:
        """Convert enum or string values into normalized strings."""

        enum_value = getattr(value, "value", value)

        return str(enum_value).casefold()


def filter_recommendations(
    recommendations: Sequence[Recommendation],
    **filters: object,
) -> list[Recommendation]:
    """Convenience function for filtering recommendations."""

    return RecommendationFilter().filter(
        recommendations,
        **filters,
    )
