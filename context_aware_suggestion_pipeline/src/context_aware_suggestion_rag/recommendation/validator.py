
"""
Recommendation validation utilities.

Provides validation for individual recommendations and collections
of recommendations.
"""

from __future__ import annotations

from collections.abc import Sequence

from context_aware_suggestion_rag.recommendation.models import (
    Recommendation,
)


class RecommendationValidator:
    """Validates recommendation objects and collections."""

    def validate(
        self,
        recommendation: Recommendation,
    ) -> bool:
        """
        Validate a single recommendation.

        Returns True when validation succeeds.
        Raises TypeError or ValueError when validation fails.
        """

        if not isinstance(recommendation, Recommendation):
            raise TypeError(
                "Expected a Recommendation instance."
            )

        self._validate_text_fields(recommendation)
        self._validate_sources(recommendation)
        self._validate_score(recommendation)
        self._validate_keywords(recommendation)
        self._validate_metadata(recommendation)

        return True

    def validate_many(
        self,
        recommendations: Sequence[Recommendation],
    ) -> bool:
        """
        Validate a collection of recommendations.

        Also checks that recommendation IDs are unique.
        """

        if isinstance(recommendations, (str, bytes)):
            raise TypeError(
                "Expected a sequence of recommendations."
            )

        if not isinstance(recommendations, Sequence):
            raise TypeError(
                "Recommendations must be a sequence."
            )

        seen_ids: set[str] = set()

        for recommendation in recommendations:
            self.validate(recommendation)

            if recommendation.id in seen_ids:
                raise ValueError(
                    f"Duplicate recommendation ID: "
                    f"{recommendation.id}"
                )

            seen_ids.add(recommendation.id)

        return True

    @staticmethod
    def _validate_text_fields(
        recommendation: Recommendation,
    ) -> None:
        """Validate required textual fields."""

        required_fields = {
            "id": recommendation.id,
            "title": recommendation.title,
            "description": recommendation.description,
            "rationale": recommendation.rationale,
            "content_format": recommendation.content_format,
            "target_audience": recommendation.target_audience,
            "priority": recommendation.priority,
        }

        for field_name, value in required_fields.items():
            if not isinstance(value, str):
                raise TypeError(
                    f"{field_name} must be a string."
                )

            if not value.strip():
                raise ValueError(
                    f"{field_name} cannot be empty."
                )

    @staticmethod
    def _validate_sources(
        recommendation: Recommendation,
    ) -> None:
        """Validate recommendation source references."""

        if not recommendation.source_ids:
            raise ValueError(
                "A recommendation must contain at least one source ID."
            )

        for source_id in recommendation.source_ids:
            if not isinstance(source_id, str):
                raise TypeError(
                    "Source IDs must be strings."
                )

            if not source_id.strip():
                raise ValueError(
                    "Source IDs cannot be empty."
                )

        for source_type in recommendation.source_types:
            if not isinstance(source_type, str):
                raise TypeError(
                    "Source types must be strings."
                )

            if not source_type.strip():
                raise ValueError(
                    "Source types cannot be empty."
                )

    @staticmethod
    def _validate_score(
        recommendation: Recommendation,
    ) -> None:
        """Validate the recommendation's overall score."""

        score = recommendation.score

        if score is None:
            raise ValueError(
                "Recommendation score is required."
            )

        if not 0.0 <= score.overall <= 1.0:
            raise ValueError(
                "Overall score must be between 0 and 1."
            )

    @staticmethod
    def _validate_keywords(
        recommendation: Recommendation,
    ) -> None:
        """Validate recommendation keywords and topics."""

        for field_name, values in (
            ("keywords", recommendation.keywords),
            ("topics", recommendation.topics),
        ):
            if not isinstance(values, list):
                raise TypeError(
                    f"{field_name} must be a list."
                )

            for value in values:
                if not isinstance(value, str):
                    raise TypeError(
                        f"Every {field_name} item must be a string."
                    )

                if not value.strip():
                    raise ValueError(
                        f"{field_name} cannot contain empty values."
                    )

    @staticmethod
    def _validate_metadata(
        recommendation: Recommendation,
    ) -> None:
        """Validate recommendation metadata."""

        if not isinstance(recommendation.metadata, dict):
            raise TypeError(
                "Recommendation metadata must be a dictionary."
            )


def validate_recommendation(
    recommendation: Recommendation,
) -> bool:
    """Convenience function for validating one recommendation."""

    return RecommendationValidator().validate(recommendation)


def validate_recommendations(
    recommendations: Sequence[Recommendation],
) -> bool:
    """Convenience function for validating recommendations."""

    return RecommendationValidator().validate_many(
        recommendations
    )
