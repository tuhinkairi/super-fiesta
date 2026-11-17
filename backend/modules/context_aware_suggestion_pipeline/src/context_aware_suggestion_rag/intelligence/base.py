"""
Base interfaces for external intelligence providers.

All trend and news providers should follow these interfaces.
"""

from abc import abstractmethod
from typing import Any

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.core.base import BaseProvider
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.intelligence.models import (
    NewsData,
    TrendData,
)


class BaseIntelligenceProvider(BaseProvider):
    """Common base class for intelligence providers."""

    @abstractmethod
    def health_check(self) -> bool:
        """Check whether the provider is operational."""
        raise NotImplementedError


class BaseTrendProvider(BaseIntelligenceProvider):
    """Interface for providers that collect trending topics."""

    @abstractmethod
    def fetch_trends(
        self,
        *,
        region: str = "IN",
        language: str = "en",
        timeframe: str = "now 7-d",
        limit: int = 20,
    ) -> list[TrendData]:
        """Fetch trending topics for a given region and timeframe."""
        raise NotImplementedError

    @abstractmethod
    def fetch_related_queries(
        self,
        keyword: str,
        *,
        region: str = "IN",
        limit: int = 10,
    ) -> list[str]:
        """Fetch related queries for a keyword."""
        raise NotImplementedError


class BaseNewsProvider(BaseIntelligenceProvider):
    """Interface for providers that collect news articles."""

    @abstractmethod
    def fetch_news(
        self,
        *,
        query: str | None = None,
        region: str = "IN",
        language: str = "en",
        limit: int = 30,
    ) -> list[NewsData]:
        """Fetch news articles, optionally filtered by a query."""
        raise NotImplementedError


class BaseIntelligenceAggregator(BaseIntelligenceProvider):
    """Interface for aggregating data from multiple providers."""

    @abstractmethod
    def collect(
        self,
        *,
        region: str = "IN",
        language: str = "en",
        query: str | None = None,
    ) -> dict[str, Any]:
        """Collect and aggregate intelligence from multiple sources."""
        raise NotImplementedError
