"""Factory functions for observability components."""

from __future__ import annotations

from .event_logger import InMemoryEventLogger
from .metrics import InMemoryMetricsProvider
from .monitoring import ApplicationMonitor
from .tracing import InMemoryTracingProvider


def create_metrics_provider(
    *,
    max_records: int = 10_000,
) -> InMemoryMetricsProvider:
    """Create an in-memory metrics provider."""
    return InMemoryMetricsProvider(max_records=max_records)


def create_tracing_provider(
    *,
    max_spans: int = 10_000,
) -> InMemoryTracingProvider:
    """Create an in-memory tracing provider."""
    return InMemoryTracingProvider(max_spans=max_spans)


def create_event_logger(
    *,
    max_events: int = 10_000,
) -> InMemoryEventLogger:
    """Create an in-memory event logger."""
    return InMemoryEventLogger(max_events=max_events)


def create_application_monitor(
    *,
    metrics_provider: InMemoryMetricsProvider | None = None,
    tracing_provider: InMemoryTracingProvider | None = None,
    event_logger: InMemoryEventLogger | None = None,
) -> ApplicationMonitor:
    """Create an application monitor with optional custom providers."""
    return ApplicationMonitor(
        metrics=metrics_provider or create_metrics_provider(),
        tracing=tracing_provider or create_tracing_provider(),
        event_logger=event_logger or create_event_logger(),
    )
