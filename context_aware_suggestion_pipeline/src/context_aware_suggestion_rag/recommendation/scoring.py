"""
Recommendation scoring engine.

Calculates weighted recommendation quality scores using relevance,
freshness, popularity, engagement potential, and source quality.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

from .models import RecommendationScore


@dataclass(frozen=True, slots=True)
class ScoringWeights:
    """Weights assigned to recommendation scoring dimensions."""

    relevance: float = 0.35
    freshness: float = 0.20
    popularity: float = 0.10
    engagement_potential: float = 0.20
    source_quality: float = 0.15

    def __post_init__(self) -> None:
        """Validate scoring weights."""
        values = (
            self.relevance,
            self.freshness,
            self.popularity,
            self.engagement_potential,
            self.source_quality,
        )

        if any(
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(value)
            or value < 0
            for value in values
        ):
            raise ValueError(
                "Scoring weights must be finite, non-negative numbers."
            )

        if not math.isclose(sum(values), 1.0, abs_tol=1e-9):
            raise ValueError("Scoring weights must sum to 1.0.")


class RecommendationScorer:
    """Calculate weighted scores for content recommendations."""

    def __init__(
        self,
        weights: ScoringWeights | None = None,
    ) -> None:
        self.weights = weights or ScoringWeights()

    @staticmethod
    def _validate_score(value: float, field_name: str) -> float:
        """Validate and normalize an individual scoring value."""
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

        return float(value)

    def calculate(
        self,
        relevance: float,
        freshness: float,
        popularity: float,
        engagement_potential: float,
        source_quality: float,
    ) -> RecommendationScore:
        """Calculate all scoring dimensions and the overall score."""
        values = {
            "relevance": self._validate_score(relevance, "relevance"),
            "freshness": self._validate_score(freshness, "freshness"),
            "popularity": self._validate_score(popularity, "popularity"),
            "engagement_potential": self._validate_score(
                engagement_potential,
                "engagement_potential",
            ),
            "source_quality": self._validate_score(
                source_quality,
                "source_quality",
            ),
        }

        weights = self.weights

        overall = (
            values["relevance"] * weights.relevance
            + values["freshness"] * weights.freshness
            + values["popularity"] * weights.popularity
            + values["engagement_potential"] * weights.engagement_potential
            + values["source_quality"] * weights.source_quality
        )

        return RecommendationScore(
            relevance=values["relevance"],
            freshness=values["freshness"],
            popularity=values["popularity"],
            engagement_potential=values["engagement_potential"],
            source_quality=values["source_quality"],
            overall=round(overall, 6),
        )

    def calculate_from_mapping(
        self,
        scores: dict[str, float],
    ) -> RecommendationScore:
        """Calculate a score from a dictionary of scoring dimensions."""
        required_fields = {
            "relevance",
            "freshness",
            "popularity",
            "engagement_potential",
            "source_quality",
        }

        missing = required_fields - scores.keys()

        if missing:
            raise ValueError(
                f"Missing scoring dimensions: {sorted(missing)}"
            )

        return self.calculate(
            relevance=scores["relevance"],
            freshness=scores["freshness"],
            popularity=scores["popularity"],
            engagement_potential=scores["engagement_potential"],
            source_quality=scores["source_quality"],
        )


def calculate_recommendation_score(
    relevance: float,
    freshness: float,
    popularity: float,
    engagement_potential: float,
    source_quality: float,
) -> RecommendationScore:
    """Convenience function for calculating a recommendation score."""
    scorer = RecommendationScorer()

    return scorer.calculate(
        relevance=relevance,
        freshness=freshness,
        popularity=popularity,
        engagement_potential=engagement_potential,
        source_quality=source_quality,
    )
