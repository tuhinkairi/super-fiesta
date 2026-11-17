"""
Intelligence provider interfaces.

Defines common contracts for trend and news data providers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any

from context_aware_suggestion_rag.intelligence.models import (
    NewsData,
    TrendData,
)


class IntelligenceProvider(ABC):
    """Base interface for intelligence data providers."""

    @abstractmethod
    def connect(self) -> None:
        """Initialize the provider."""
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> bool:
        """Check provider availability."""
        raise NotImplementedError

    def close(self) -> None:
        """Release provider resources."""
        return None


class TrendProvider(ABC):
    """Interface for trend collection providers."""

    @abstractmethod
    def fetch_trends(
        self,
        keywords: Sequence[str] | None = None,
        region: str = "IN",
        timeframe: str = "now 7-d",
        category: int = 0,
        limit: int = 20,
    ) -> list[TrendData]:
        """Collect trend information."""
        raise NotImplementedError

    @abstractmethod
    def fetch_related_queries(
        self,
        keyword: str,
    ) -> dict[str, Any]:
        """Collect queries related to a keyword."""
        raise NotImplementedError


class NewsProvider(ABC):
    """Interface for news collection providers."""

    @abstractmethod
    def fetch_news(
        self,
        query: str | None = None,
        limit: int = 30,
        lookback_hours: int = 72,
    ) -> list[NewsData]:
        """Collect news articles."""
        raise NotImplementedError
