
from datetime import datetime, timezone
from types import SimpleNamespace

from context_aware_suggestion_rag.recommendation.models import (
    Recommendation,
    RecommendationScore,
)
from context_aware_suggestion_rag.recommendation.ranking import (
    RecommendationRanker,
    rank_recommendations,
)


def make_recommendation(
    recommendation_id: str,
    overall: float,
    priority: str,
    freshness: float = 0.8,
) -> Recommendation:
    recommendation = object.__new__(Recommendation)

    score = RecommendationScore(
        relevance=overall,
        freshness=freshness,
        popularity=0.7,
        engagement_potential=0.8,
        source_quality=0.9,
        overall=overall,
    )

    object.__setattr__(recommendation, "id", recommendation_id)
    object.__setattr__(recommendation, "score", score)
    object.__setattr__(recommendation, "priority", priority)
    object.__setattr__(
        recommendation,
        "created_at",
        datetime.now(timezone.utc),
    )

    return recommendation


first = make_recommendation("rec-1", 0.70, "high")
second = make_recommendation("rec-2", 0.95, "low")
third = make_recommendation("rec-3", 0.80, "critical")

ranker = RecommendationRanker()

ranked = ranker.rank([first, second, third])

print("Ranking:", [item.id for item in ranked])

limited = rank_recommendations([first, second, third], limit=2)

print("Top two:", [item.id for item in limited])

empty = ranker.rank([])

print("Empty ranking:", empty)
