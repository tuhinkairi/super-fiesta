"""
Intelligence service.

Provides a unified application-level interface for collecting
external trends and news.
"""

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.core.logging import get_logger
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.intelligence.aggregator import (
    IntelligenceAggregator,
)
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.intelligence.models import (
    IntelligenceCollectionResult,
)
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.intelligence.news import RSSNewsProvider
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.intelligence.trends import (
    GoogleTrendsProvider,
)

logger = get_logger(__name__)


class IntelligenceService:
    """Application service for external intelligence collection."""

    def __init__(
        self,
        aggregator: IntelligenceAggregator | None = None,
    ) -> None:
        if aggregator is None:
            aggregator = IntelligenceAggregator(
                trend_provider=GoogleTrendsProvider(),
                news_provider=RSSNewsProvider(),
            )

        self.aggregator = aggregator

    def collect(
        self,
        *,
        region: str = "IN",
        language: str = "en",
        query: str | None = None,
        trend_limit: int = 20,
        news_limit: int = 30,
    ) -> IntelligenceCollectionResult:
        """Collect trends and news."""
        if not isinstance(region, str) or not region.strip():
            raise ValueError("region cannot be empty")

        if not isinstance(language, str) or not language.strip():
            raise ValueError("language cannot be empty")

        if query is not None:
            if not isinstance(query, str) or not query.strip():
                raise ValueError("query cannot be empty when provided")

        if (
            isinstance(trend_limit, bool)
            or not isinstance(trend_limit, int)
            or trend_limit < 1
        ):
            raise ValueError("trend_limit must be a positive integer")

        if (
            isinstance(news_limit, bool)
            or not isinstance(news_limit, int)
            or news_limit < 1
        ):
            raise ValueError("news_limit must be a positive integer")

        logger.info(
            "Starting intelligence collection for region=%s, query=%s",
            region,
            query,
        )

        result = self.aggregator.collect(
            region=region,
            language=language,
            query=query,
            trend_limit=trend_limit,
            news_limit=news_limit,
        )

        logger.info(
            "Intelligence collection completed: trends=%d, news=%d, "
            "success=%s",
            len(result.trends),
            len(result.news),
            result.success,
        )

        return result

    def close(self) -> None:
        """Close the underlying intelligence providers."""
        self.aggregator.close()


_default_service: IntelligenceService | None = None


def get_intelligence_service() -> IntelligenceService:
    """Return a reusable default intelligence service."""
    global _default_service

    if _default_service is None:
        _default_service = IntelligenceService()

    return _default_service


def collect_intelligence(
    *,
    region: str = "IN",
    language: str = "en",
    query: str | None = None,
    trend_limit: int = 20,
    news_limit: int = 30,
) -> IntelligenceCollectionResult:
    """Convenience function for collecting intelligence."""
    return get_intelligence_service().collect(
        region=region,
        language=language,
        query=query,
        trend_limit=trend_limit,
        news_limit=news_limit,
    )
