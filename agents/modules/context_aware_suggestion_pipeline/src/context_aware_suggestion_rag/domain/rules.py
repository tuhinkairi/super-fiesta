"""
Domain business rules.

Contains reusable business-rule checks for documents,
recommendations, generated content, and source references.
"""

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.domain.entities import (
    DocumentEntity,
    GeneratedContentEntity,
    RecommendationEntity,
    TrendEntity,
)


class DomainRuleViolation(ValueError):
    """Raised when a domain business rule is violated."""


def validate_document_for_processing(
    document: DocumentEntity,
) -> None:
    """Ensure a document is suitable for downstream processing."""

    if not isinstance(document, DocumentEntity):
        raise DomainRuleViolation(
            "Expected a DocumentEntity instance."
        )

    if not document.content.strip():
        raise DomainRuleViolation(
            "Document content cannot be empty."
        )

    if not document.filename.strip():
        raise DomainRuleViolation(
            "Document filename cannot be empty."
        )


def validate_trend(trend: TrendEntity) -> None:
    """Ensure a trend contains meaningful information."""

    if not isinstance(trend, TrendEntity):
        raise DomainRuleViolation(
            "Expected a TrendEntity instance."
        )

    if not trend.title.strip():
        raise DomainRuleViolation(
            "Trend title cannot be empty."
        )

    if trend.trend_score is not None and trend.trend_score < 0:
        raise DomainRuleViolation(
            "Trend score cannot be negative."
        )


def validate_recommendation(
    recommendation: RecommendationEntity,
) -> None:
    """Ensure a recommendation is suitable for delivery."""

    if not isinstance(recommendation, RecommendationEntity):
        raise DomainRuleViolation(
            "Expected a RecommendationEntity instance."
        )

    if not recommendation.title.strip():
        raise DomainRuleViolation(
            "Recommendation title cannot be empty."
        )

    if not recommendation.description.strip():
        raise DomainRuleViolation(
            "Recommendation description cannot be empty."
        )

    if not recommendation.rationale.strip():
        raise DomainRuleViolation(
            "Recommendation rationale cannot be empty."
        )

    if not recommendation.source_ids:
        raise DomainRuleViolation(
            "A recommendation must reference at least one source."
        )

    if len(recommendation.source_ids) != len(
        set(recommendation.source_ids)
    ):
        raise DomainRuleViolation(
            "Recommendation source IDs must be unique."
        )


def validate_generated_content(
    content: GeneratedContentEntity,
) -> None:
    """Ensure generated content is linked and ready for delivery."""

    if not isinstance(content, GeneratedContentEntity):
        raise DomainRuleViolation(
            "Expected a GeneratedContentEntity instance."
        )

    if not content.recommendation_id.strip():
        raise DomainRuleViolation(
            "Generated content must reference a recommendation."
        )

    if not content.title.strip():
        raise DomainRuleViolation(
            "Generated content title cannot be empty."
        )

    if not content.body.strip():
        raise DomainRuleViolation(
            "Generated content body cannot be empty."
        )


def validate_recommendation_content_link(
    recommendation: RecommendationEntity,
    content: GeneratedContentEntity,
) -> None:
    """Ensure generated content belongs to the supplied recommendation."""

    validate_recommendation(recommendation)
    validate_generated_content(content)

    if content.recommendation_id != recommendation.recommendation_id:
        raise DomainRuleViolation(
            "Generated content references a different recommendation."
        )

    if content.content_format != recommendation.content_format:
        raise DomainRuleViolation(
            "Generated content format does not match the recommendation."
        )


__all__ = [
    "DomainRuleViolation",
    "validate_document_for_processing",
    "validate_trend",
    "validate_recommendation",
    "validate_generated_content",
    "validate_recommendation_content_link",
]
