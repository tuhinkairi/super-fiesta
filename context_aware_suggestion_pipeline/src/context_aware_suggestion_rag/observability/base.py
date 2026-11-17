"""Base interfaces for observability components."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from .models import MetricRecord, ObservabilityEvent, TraceSpan


class BaseObservabilityProvider(ABC):
    """Base contract for observability providers."""

    @abstractmethod
    def connect(self) -> None:
        """Initialize the provider."""
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> bool:
        """Check whether the provider is operational."""
        raise NotImplementedError

    def close(self) -> None:
        """Release provider resources."""
        return None


class BaseMetricsProvider(BaseObservabilityProvider):
    """Abstract interface for metrics collection."""

    @abstractmethod
    def increment(
        self,
        name: str,
        value: float = 1.0,
        labels: dict[str, str] | None = None,
    ) -> MetricRecord:
        """Increment a counter metric."""
        raise NotImplementedError

    @abstractmethod
    def gauge(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> MetricRecord:
        """Record a gauge metric."""
        raise NotImplementedError

    @abstractmethod
    def timing(
        self,
        name: str,
        duration_ms: float,
        labels: dict[str, str] | None = None,
    ) -> MetricRecord:
        """Record a timing metric."""
        raise NotImplementedError

    @abstractmethod
    def get_metrics(
        self,
        name: str | None = None,
    ) -> list[MetricRecord]:
        """Retrieve recorded metrics."""
        raise NotImplementedError


class BaseTracingProvider(BaseObservabilityProvider):
    """Abstract interface for tracing operations."""

    @abstractmethod
    def start_span(
        self,
        name: str,
        parent_span_id: str | None = None,
        trace_id: str | None = None,
        attributes: dict[str, Any] | None = None,
    ) -> TraceSpan:
        """Start a new trace span."""
        raise NotImplementedError

    @abstractmethod
    def end_span(
        self,
        span_id: str,
        status: str = "ok",
        error: str | None = None,
    ) -> TraceSpan:
        """Finish an active trace span."""
        raise NotImplementedError

    @abstractmethod
    def get_span(self, span_id: str) -> TraceSpan | None:
        """Retrieve a span by its identifier."""
        raise NotImplementedError

    @abstractmethod
    def get_trace(self, trace_id: str) -> list[TraceSpan]:
        """Retrieve all spans belonging to a trace."""
        raise NotImplementedError


class BaseEventLogger(BaseObservabilityProvider):
    """Abstract interface for structured event logging."""

    @abstractmethod
    def log_event(
        self,
        name: str,
        message: str,
        level: str = "INFO",
        attributes: dict[str, Any] | None = None,
        trace_id: str | None = None,
        span_id: str | None = None,
    ) -> ObservabilityEvent:
        """Record a structured observability event."""
        raise NotImplementedError

    @abstractmethod
    def get_events(
        self,
        name: str | None = None,
        level: str | None = None,
        limit: int | None = None,
    ) -> list[ObservabilityEvent]:
        """Retrieve recorded events."""
        raise NotImplementedError
