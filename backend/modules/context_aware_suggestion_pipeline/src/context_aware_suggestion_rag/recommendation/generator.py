"""
Recommendation generation utilities.

Converts structured recommendation candidates into Recommendation
domain objects with calculated scores and generated identifiers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence
from uuid import uuid4

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.recommendation.models import (
    Recommendation,
    RecommendationCategory,
    RecommendationScore,
    RecommendationStatus,
)


@dataclass(slots=True)
class RecommendationCandidate:
    """Input data required to create a recommendation."""

    title: str
    description: str
    rationale: str
    category: RecommendationCategory
    content_format: str
    target_audience: str

    keywords: list[str] = field(default_factory=list)
    topics: list[str] = field(default_factory=list)
    source_ids: list[str] = field(default_factory=list)
    source_types: list[str] = field(default_factory=list)

    relevance: float = 0.5
    freshness: float = 0.5
    popularity: float = 0.5
    engagement_potential: float = 0.5
    source_quality: float = 0.5

    priority: str = "medium"
    metadata: dict[str, object] = field(default_factory=dict)


class RecommendationGenerator:
    """Generates Recommendation objects from candidate data."""

    def generate(
        self,
        candidates: Sequence[RecommendationCandidate],
    ) -> list[Recommendation]:
        """
        Generate recommendations from candidate objects.

        Each candidate is converted into a Recommendation with
        a calculated overall score and a unique identifier.
        """

        if isinstance(candidates, (str, bytes)):
            raise TypeError(
                "Candidates must be a sequence of RecommendationCandidate objects."
            )

        if not isinstance(candidates, Sequence):
            raise TypeError(
                "Candidates must be a sequence."
            )

        recommendations: list[Recommendation] = []

        for candidate in candidates:
            if not isinstance(candidate, RecommendationCandidate):
                raise TypeError(
                    "Every candidate must be a RecommendationCandidate."
                )

            score = self._calculate_score(candidate)

            recommendation = Recommendation(
                id=self._generate_id(),
                title=candidate.title,
                description=candidate.description,
                rationale=candidate.rationale,
                category=candidate.category,
                content_format=candidate.content_format,
                target_audience=candidate.target_audience,
                keywords=list(candidate.keywords),
                topics=list(candidate.topics),
                source_ids=list(candidate.source_ids),
                source_types=list(candidate.source_types),
                score=score,
                status=RecommendationStatus.PENDING,
                priority=candidate.priority,
                metadata=dict(candidate.metadata),
            )

            recommendations.append(recommendation)

        return recommendations

    @staticmethod
    def _calculate_score(
        candidate: RecommendationCandidate,
    ) -> RecommendationScore:
        """Calculate the weighted overall recommendation score."""

        components = {
            "relevance": candidate.relevance,
            "freshness": candidate.freshness,
            "popularity": candidate.popularity,
            "engagement_potential": candidate.engagement_potential,
            "source_quality": candidate.source_quality,
        }

        for name, value in components.items():
            if isinstance(value, bool) or not isinstance(
                value, (int, float)
            ):
                raise TypeError(
                    f"{name} must be numeric."
                )

            if not 0.0 <= value <= 1.0:
                raise ValueError(
                    f"{name} must be between 0 and 1."
                )

        overall = (
            candidate.relevance * 0.35
            + candidate.freshness * 0.20
            + candidate.popularity * 0.10
            + candidate.engagement_potential * 0.20
            + candidate.source_quality * 0.15
        )

        return RecommendationScore(
            relevance=candidate.relevance,
            freshness=candidate.freshness,
            popularity=candidate.popularity,
            engagement_potential=candidate.engagement_potential,
            source_quality=candidate.source_quality,
            overall=overall,
        )

    @staticmethod
    def _generate_id() -> str:
        """Generate a unique recommendation identifier."""

        return f"rec_{uuid4().hex}"
