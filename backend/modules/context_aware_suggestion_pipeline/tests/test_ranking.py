
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from context_aware_suggestion_rag.recommendation.ranking import (
    RecommendationRanker,
)


def create_recommendation(name, score, priority, created_at):
    return SimpleNamespace(
        id=name,
        score=SimpleNamespace(overall=score),
        priority=priority,
        created_at=created_at,
    )


def test_ranking_by_overall_score():
    ranker = RecommendationRanker()
    now = datetime.now(timezone.utc)

    recommendations = [
        create_recommendation("A", 0.70, "high", now),
        create_recommendation("B", 0.95, "low", now),
        create_recommendation("C", 0.85, "medium", now),
    ]

    ranked = sorted(
        recommendations,
        key=ranker._ranking_key,
        reverse=True,
    )

    assert [item.id for item in ranked] == ["B", "C", "A"]


def test_ranking_by_priority_when_scores_are_equal():
    ranker = RecommendationRanker()
    now = datetime.now(timezone.utc)

    recommendations = [
        create_recommendation("A", 0.90, "low", now),
        create_recommendation("B", 0.90, "critical", now),
        create_recommendation("C", 0.90, "medium", now),
    ]

    ranked = sorted(
        recommendations,
        key=ranker._ranking_key,
        reverse=True,
    )

    assert [item.id for item in ranked] == ["B", "C", "A"]


def test_ranking_by_creation_time():
    ranker = RecommendationRanker()
    now = datetime.now(timezone.utc)

    recommendations = [
        create_recommendation("A", 0.90, "high", now),
        create_recommendation(
            "B", 0.90, "high", now + timedelta(days=1)
        ),
    ]

    ranked = sorted(
        recommendations,
        key=ranker._ranking_key,
        reverse=True,
    )

    assert [item.id for item in ranked] == ["B", "A"]


def test_limit_validation():
    ranker = RecommendationRanker()

    with pytest.raises(ValueError):
        ranker.rank([], limit=0)

    with pytest.raises(TypeError):
        ranker.rank([], limit=True)
