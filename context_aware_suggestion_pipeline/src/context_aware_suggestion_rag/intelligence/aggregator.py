"""
Intelligence aggregation service.

Combines trend and news providers into a unified collection result.
Individual provider failures are recorded without preventing the
other provider from returning useful information.
"""

from datetime import datetime, timezone

from context_aware_suggestion_rag.core.logging import get_logger
from context_aware_suggestion_rag.intelligence.base import (
    BaseNewsProvider,
    BaseTrendProvider,
)
from context_aware_suggestion_rag.intelligence.models import (
    IntelligenceCollectionResult,
)

logger = get_logger(__name__)


class IntelligenceAggregator:
    """Aggregate trends and news from multiple providers."""

    def __init__(
        self,
        *,
        trend_provider: BaseTrendProvider | None = None,
        news_provider: BaseNewsProvider | None = None,
    ) -> None:
        self.trend_provider = trend_provider
        self.news_provider = news_provider

    def collect(
        self,
        *,
        region: str = "IN",
        language: str = "en",
        query: str | None = None,
        trend_limit: int = 20,
        news_limit: int = 30,
    ) -> IntelligenceCollectionResult:
        """
        Collect trends and news from available providers.

        A failure in one provider does not prevent collection
        from the other provider.
        """
        started_at = datetime.now(timezone.utc)

        trends = []
        news = []
        warnings: list[str] = []

        provider_names: list[str] = []

        if self.trend_provider is not None:
            provider_names.append("google_trends")

            try:
                trends = self.trend_provider.fetch_trends(
                    region=region,
                    language=language,
                    limit=trend_limit,
                )

                if query:
                    related_queries = (
                        self.trend_provider.fetch_related_queries(
                            query,
                            region=region,
                            limit=10,
                        )
                    )

                    for trend in trends:
                        trend.related_queries = list(
                            dict.fromkeys(
                                trend.related_queries + related_queries
                            )
                        )

                logger.info(
                    "Collected %d trends",
                    len(trends),
                )

            except Exception as exc:
                warning = f"Trend collection failed: {exc}"
                warnings.append(warning)
                logger.exception(warning)

        if self.news_provider is not None:
            provider_names.append("rss_news")

            try:
                news = self.news_provider.fetch_news(
                    query=query,
                    region=region,
                    language=language,
                    limit=news_limit,
                )

                logger.info(
                    "Collected %d news articles",
                    len(news),
                )

            except Exception as exc:
                warning = f"News collection failed: {exc}"
                warnings.append(warning)
                logger.exception(warning)

        completed_at = datetime.now(timezone.utc)

        duration = (
            completed_at - started_at
        ).total_seconds()

        provider_name = (
            "+".join(provider_names)
            if provider_names
            else "none"
        )

        success = not warnings

        return IntelligenceCollectionResult(
            provider=provider_name,
            collection_type="combined",
            trends=trends,
            news=news,
            collected_at=completed_at,
            duration_seconds=duration,
            success=success,
            warnings=warnings,
            metadata={
                "region": region,
                "language": language,
                "query": query,
                "trend_count": len(trends),
                "news_count": len(news),
                "providers": provider_names,
                "started_at": started_at.isoformat(),
            },
        )

    def close(self) -> None:
        """Close providers that expose a close method."""
        for provider in (
            self.trend_provider,
            self.news_provider,
        ):
            if provider is None:
                continue

            close_method = getattr(provider, "close", None)

            if callable(close_method):
                try:
                    close_method()
                except Exception:
                    logger.exception(
                        "Failed to close provider %s",
                        type(provider).__name__,
                    )
