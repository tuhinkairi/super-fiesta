"""
Recommendation module.

Provides recommendation models, scoring, ranking, filtering,
generation, validation, selection, diversification, configuration,
and service orchestration.
"""

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.recommendation.models import (
    Recommendation,
    RecommendationCategory,
    RecommendationScore,
    RecommendationStatus,
)

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.recommendation.scoring import (
    RecommendationScorer,
    ScoringWeights,
    calculate_recommendation_score,
)

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.recommendation.ranking import (
    RecommendationRanker,
    rank_recommendations,
)

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.recommendation.filters import (
    RecommendationFilter,
    filter_recommendations,
)

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.recommendation.generator import (
    RecommendationCandidate,
    RecommendationGenerator,
)

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.recommendation.validator import (
    RecommendationValidator,
    validate_recommendation,
    validate_recommendations,
)

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.recommendation.selector import (
    RecommendationSelector,
    select_recommendations,
)

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.recommendation.diversifier import (
    RecommendationDiversifier,
    diversify_recommendations,
)

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.recommendation.config import (
    RecommendationConfig,
    get_recommendation_config,
)

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.recommendation.service import (
    RecommendationService,
    create_recommendation_service,
)


__all__ = [
    # Models
    "Recommendation",
    "RecommendationCategory",
    "RecommendationScore",
    "RecommendationStatus",

    # Scoring
    "RecommendationScorer",
    "ScoringWeights",
    "calculate_recommendation_score",

    # Ranking
    "RecommendationRanker",
    "rank_recommendations",

    # Filtering
    "RecommendationFilter",
    "filter_recommendations",

    # Generation
    "RecommendationCandidate",
    "RecommendationGenerator",

    # Validation
    "RecommendationValidator",
    "validate_recommendation",
    "validate_recommendations",

    # Selection
    "RecommendationSelector",
    "select_recommendations",

    # Diversification
    "RecommendationDiversifier",
    "diversify_recommendations",

    # Configuration
    "RecommendationConfig",
    "get_recommendation_config",

    # Service
    "RecommendationService",
    "create_recommendation_service",
]
