"""
External intelligence collection package.

Provides standardized models, provider interfaces, Google Trends
integration, RSS news collection, aggregation, and service APIs.
"""

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.intelligence.models import (
    IntelligenceModel,
    TrendData,
    NewsData,
    IntelligenceCollectionResult,
    current_utc_time,
)

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.intelligence.base import (
    BaseIntelligenceProvider,
    BaseTrendProvider,
    BaseNewsProvider,
    BaseIntelligenceAggregator,
)

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.intelligence.trends import (
    GoogleTrendsProvider,
)

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.intelligence.news import (
    RSSNewsProvider,
)

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.intelligence.aggregator import (
    IntelligenceAggregator,
)

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.intelligence.service import (
    IntelligenceService,
    get_intelligence_service,
    collect_intelligence,
)


__all__ = [
    # Models
    "IntelligenceModel",
    "TrendData",
    "NewsData",
    "IntelligenceCollectionResult",
    "current_utc_time",

    # Provider interfaces
    "BaseIntelligenceProvider",
    "BaseTrendProvider",
    "BaseNewsProvider",
    "BaseIntelligenceAggregator",

    # Providers
    "GoogleTrendsProvider",
    "RSSNewsProvider",

    # Aggregation
    "IntelligenceAggregator",

    # Service
    "IntelligenceService",
    "get_intelligence_service",
    "collect_intelligence",
]
