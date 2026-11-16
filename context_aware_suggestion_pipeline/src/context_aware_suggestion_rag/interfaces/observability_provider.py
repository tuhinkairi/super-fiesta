"""
Observability provider interfaces.

Defines contracts for metrics, tracing, and monitoring integrations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any


class ObservabilityProvider(ABC):
    """Base contract for observability implementations."""

    @abstractmethod
    def health_check(self) -> bool:
        """Check whether the observability provider is operational."""
        raise NotImplementedError

    def close(self) -> None:
        """Release provider resources when applicable."""
        return None


class MetricsProvider(ObservabilityProvider):
    """Interface for recording application metrics."""

    @abstractmethod
    def increment(
        self,
        name: str,
        value: int | float = 1,
        tags: Mapping[str, str] | None = None,
    ) -> None:
        """Increment a metric by a numeric value."""
        raise NotImplementedError

    @abstractmethod
    def gauge(
        self,
        name: str,
        value: int | float,
        tags: Mapping[str, str] | None = None,
    ) -> None:
        """Record a gauge metric."""
        raise NotImplementedError

    @abstractmethod
    def timing(
        self,
        name: str,
        duration_ms: float,
        tags: Mapping[str, str] | None = None,
    ) -> None:
        """Record an operation duration."""
        raise NotImplementedError


class TracingProvider(ObservabilityProvider):
    """Interface for distributed tracing integrations."""

    @abstractmethod
    def start_span(
        self,
        name: str,
        attributes: Mapping[str, Any] | None = None,
    ) -> Any:
        """Start and return a tracing span."""
        raise NotImplementedError

    @abstractmethod
    def end_span(self, span: Any) -> None:
        """Finish an active tracing span."""
        raise NotImplementedError
