"""
Recommendation diversification utilities.

Reduces repetitive recommendations by applying configurable limits
to categories, topics, and content formats.

The input order is preserved, so pass ranked recommendations when
ranking-based selection is desired.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.recommendation.models import (
    Recommendation,
)


class RecommendationDiversifier:
    """Diversifies recommendation collections."""

    def diversify(
        self,
        recommendations: Sequence[Recommendation],
        *,
        limit: int = 10,
        max_per_category: int | None = 3,
        max_per_topic: int | None = 3,
        max_per_content_format: int | None = 5,
    ) -> list[Recommendation]:
        """
        Select recommendations while limiting repetition.

        The original recommendation order is preserved.

        A recommendation is skipped when adding it would exceed
        any configured category, topic, or content-format limit.
        """

        self._validate_recommendations(recommendations)

        self._validate_limit("limit", limit, allow_none=False)
        self._validate_limit(
            "max_per_category", max_per_category
        )
        self._validate_limit("max_per_topic", max_per_topic)
        self._validate_limit(
            "max_per_content_format",
            max_per_content_format,
        )

        category_counts: Counter[str] = Counter()
        topic_counts: Counter[str] = Counter()
        format_counts: Counter[str] = Counter()

        selected: list[Recommendation] = []

        for recommendation in recommendations:
            if len(selected) >= limit:
                break

            category = self._normalize(
                recommendation.category
            )
            content_format = self._normalize(
                recommendation.content_format
            )
            topics = {
                self._normalize(topic)
                for topic in recommendation.topics
            }

            # Check category limit.
            if (
                max_per_category is not None
                and category_counts[category] >= max_per_category
            ):
                continue

            # Check content-format limit.
            if (
                max_per_content_format is not None
                and format_counts[content_format]
                >= max_per_content_format
            ):
                continue

            # Check topic limits.
            if max_per_topic is not None:
                if any(
                    topic_counts[topic] >= max_per_topic
                    for topic in topics
                ):
                    continue

            # Accept recommendation.
            selected.append(recommendation)

            category_counts[category] += 1
            format_counts[content_format] += 1

            for topic in topics:
                topic_counts[topic] += 1

        return selected

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
    def _validate_limit(
        name: str,
        value: int | None,
        *,
        allow_none: bool = True,
    ) -> None:
        """Validate a selection limit."""

        if value is None:
            if allow_none:
                return

            raise ValueError(f"{name} cannot be None.")

        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"{name} must be an integer.")

        if value <= 0:
            raise ValueError(
                f"{name} must be greater than zero."
            )

    @staticmethod
    def _normalize(value: object) -> str:
        """Normalize enum and string values."""

        enum_value = getattr(value, "value", value)
        return str(enum_value).strip().casefold()


def diversify_recommendations(
    recommendations: Sequence[Recommendation],
    *,
    limit: int = 10,
    max_per_category: int | None = 3,
    max_per_topic: int | None = 3,
    max_per_content_format: int | None = 5,
) -> list[Recommendation]:
    """Convenience function for recommendation diversification."""

    return RecommendationDiversifier().diversify(
        recommendations,
        limit=limit,
        max_per_category=max_per_category,
        max_per_topic=max_per_topic,
        max_per_content_format=max_per_content_format,
    )
