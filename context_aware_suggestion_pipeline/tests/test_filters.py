
from datetime import datetime, timezone

import pytest

from context_aware_suggestion_rag.recommendation.filters import (
    RecommendationFilter,
)
from context_aware_suggestion_rag.recommendation.models import (
    Recommendation,
    RecommendationCategory,
    RecommendationScore,
    RecommendationStatus,
)


def create_recommendation(
    title: str,
    score: float,
    category: RecommendationCategory,
    keywords: list[str],
    audience: str,
) -> Recommendation:
    return Recommendation(
        id=f"test_{title.lower().replace(' ', '_')}",
        title=title,
        description="Test recommendation description.",
        rationale="Test rationale.",
        category=category,
        content_format="article",
        target_audience=audience,
        keywords=keywords,
        topics=["technology"],
        source_ids=["source_001"],
        source_types=["document"],
        score=RecommendationScore(
            relevance=score,
            freshness=score,
            popularity=score,
            engagement_potential=score,
            source_quality=score,
            overall=score,
        ),
        status=RecommendationStatus.PENDING,
        priority="high",
        created_at=datetime.now(timezone.utc),
    )


def test_filter_by_minimum_score():
    recommendations = [
        create_recommendation(
            "AI Guide",
            0.90,
            RecommendationCategory.EDUCATIONAL,
            ["ai"],
            "students",
        ),
        create_recommendation(
            "Security Guide",
            0.60,
            RecommendationCategory.EDUCATIONAL,
            ["security"],
            "students",
        ),
    ]

    result = RecommendationFilter().filter(
        recommendations,
        min_score=0.80,
    )

    assert len(result) == 1
    assert result[0].title == "AI Guide"


def test_filter_by_category():
    recommendations = [
        create_recommendation(
            "AI Guide",
            0.90,
            RecommendationCategory.EDUCATIONAL,
            ["ai"],
            "students",
        ),
        create_recommendation(
            "News Update",
            0.80,
            RecommendationCategory.NEWS,
            ["news"],
            "professionals",
        ),
    ]

    result = RecommendationFilter().filter(
        recommendations,
        categories=["educational"],
    )

    assert len(result) == 1
    assert result[0].title == "AI Guide"


def test_filter_by_required_keywords():
    recommendations = [
        create_recommendation(
            "AI Security",
            0.90,
            RecommendationCategory.EDUCATIONAL,
            ["ai", "security"],
            "students",
        ),
        create_recommendation(
            "AI Guide",
            0.80,
            RecommendationCategory.EDUCATIONAL,
            ["ai"],
            "students",
        ),
    ]

    result = RecommendationFilter().filter(
        recommendations,
        required_keywords=["ai", "security"],
    )

    assert len(result) == 1
    assert result[0].title == "AI Security"


def test_invalid_minimum_score():
    with pytest.raises(ValueError):
        RecommendationFilter().filter([], min_score=1.5)


def test_invalid_filter_value():
    with pytest.raises(ValueError):
        RecommendationFilter().filter(
            [],
            categories=[""],
        )
