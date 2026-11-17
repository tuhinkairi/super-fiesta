
"""Application monitoring service."""

from __future__ import annotations

from typing import Any

from .event_logger import InMemoryEventLogger
from .metrics import InMemoryMetricsProvider
from .models import ObservabilityEvent, TraceSpan
from .tracing import InMemoryTracingProvider


class ApplicationMonitor:
    """Coordinates metrics, tracing, and structured event logging."""

    def __init__(
        self,
        metrics: InMemoryMetricsProvider | None = None,
        tracing: InMemoryTracingProvider | None = None,
        event_logger: InMemoryEventLogger | None = None,
    ) -> None:
        self.metrics = metrics or InMemoryMetricsProvider()
        self.tracing = tracing or InMemoryTracingProvider()
        self.event_logger = event_logger or InMemoryEventLogger()
        self._connected = False
        self._closed = False

    def connect(self) -> None:
        """Initialize all monitoring providers."""
        if self._closed:
            raise RuntimeError("Application monitor is closed.")

        connected = []

        try:
            for provider in (
                self.metrics,
                self.tracing,
                self.event_logger,
            ):
                provider.connect()
                connected.append(provider)

            self._connected = True

        except Exception:
            for provider in reversed(connected):
                try:
                    provider.close()
                except Exception:
                    pass

            self._connected = False
            raise

    def health_check(self) -> bool:
        """Check whether all monitoring providers are operational."""
        if self._closed or not self._connected:
            return False

        try:
            return all(
                provider.health_check()
                for provider in (
                    self.metrics,
                    self.tracing,
                    self.event_logger,
                )
            )
        except Exception:
            return False

    def _ensure_connected(self) -> None:
        if self._closed:
            raise RuntimeError("Application monitor is closed.")

        if not self._connected:
            self.connect()

    def record_pipeline_start(
        self,
        pipeline_name: str,
        execution_id: str,
        attributes: dict[str, Any] | None = None,
    ) -> TraceSpan:
        """Start tracking a pipeline execution."""
        self._ensure_connected()

        if not isinstance(pipeline_name, str) or not pipeline_name.strip():
            raise ValueError("Pipeline name must be non-empty.")

        if not isinstance(execution_id, str) or not execution_id.strip():
            raise ValueError("Execution ID must be non-empty.")

        span = self.tracing.start_span(
            name=f"pipeline.{pipeline_name}",
            attributes={
                "execution_id": execution_id,
                **(attributes or {}),
            },
        )

        self.metrics.increment("pipeline.executions.started")

        self.event_logger.log_event(
            name="pipeline.started",
            message=f"Pipeline '{pipeline_name}' started.",
            level="INFO",
            attributes={
                "pipeline_name": pipeline_name,
                "execution_id": execution_id,
            },
            trace_id=span.trace_id,
            span_id=span.span_id,
        )

        return span

    def record_pipeline_success(
        self,
        span_id: str,
        execution_time_ms: float,
        attributes: dict[str, Any] | None = None,
    ) -> TraceSpan:
        """Record successful pipeline completion."""
        self._ensure_connected()

        span = self.tracing.get_span(span_id)

        if span is None:
            raise KeyError(f"Pipeline span not found: {span_id}")

        if span.ended_at is not None:
            raise ValueError("Pipeline span has already ended.")

        if isinstance(execution_time_ms, bool) or not isinstance(
            execution_time_ms, (int, float)
        ):
            raise TypeError("Execution time must be numeric.")

        if execution_time_ms < 0:
            raise ValueError("Execution time cannot be negative.")

        for key, value in (attributes or {}).items():
            self.tracing.set_attribute(span_id, key, value)

        completed = self.tracing.end_span(span_id, status="ok")

        self.metrics.increment("pipeline.executions.completed")
        self.metrics.timing(
            "pipeline.execution.duration_ms",
            float(execution_time_ms),
        )

        self.event_logger.log_event(
            name="pipeline.completed",
            message="Pipeline execution completed successfully.",
            level="INFO",
            attributes={
                "execution_time_ms": float(execution_time_ms),
            },
            trace_id=completed.trace_id,
            span_id=completed.span_id,
        )

        return completed

    def record_pipeline_failure(
        self,
        span_id: str,
        error: str,
        execution_time_ms: float | None = None,
    ) -> TraceSpan:
        """Record pipeline execution failure."""
        self._ensure_connected()

        span = self.tracing.get_span(span_id)

        if span is None:
            raise KeyError(f"Pipeline span not found: {span_id}")

        if span.ended_at is not None:
            raise ValueError("Pipeline span has already ended.")

        if not isinstance(error, str) or not error.strip():
            raise ValueError("Error message must be non-empty.")

        if execution_time_ms is not None:
            if isinstance(execution_time_ms, bool) or not isinstance(
                execution_time_ms, (int, float)
            ):
                raise TypeError("Execution time must be numeric.")

            if execution_time_ms < 0:
                raise ValueError("Execution time cannot be negative.")

            self.metrics.timing(
                "pipeline.execution.duration_ms",
                float(execution_time_ms),
            )

        completed = self.tracing.end_span(
            span_id,
            status="error",
            error=error,
        )

        self.metrics.increment("pipeline.executions.failed")

        self.event_logger.log_event(
            name="pipeline.failed",
            message=error,
            level="ERROR",
            attributes={
                "execution_time_ms": execution_time_ms,
            },
            trace_id=completed.trace_id,
            span_id=completed.span_id,
        )

        return completed

    def record_custom_event(
        self,
        name: str,
        message: str,
        level: str = "INFO",
        attributes: dict[str, Any] | None = None,
        trace_id: str | None = None,
        span_id: str | None = None,
    ) -> ObservabilityEvent:
        """Record a custom application event."""
        self._ensure_connected()

        return self.event_logger.log_event(
            name=name,
            message=message,
            level=level,
            attributes=attributes,
            trace_id=trace_id,
            span_id=span_id,
        )

    def get_pipeline_metrics(self) -> dict[str, float]:
        """Return a summary of pipeline execution counters."""
        self._ensure_connected()

        return {
            "started": self.metrics.get_counter_value(
                "pipeline.executions.started"
            ),
            "completed": self.metrics.get_counter_value(
                "pipeline.executions.completed"
            ),
            "failed": self.metrics.get_counter_value(
                "pipeline.executions.failed"
            ),
        }

    def close(self) -> None:
        """Close all monitoring providers."""
        if self._closed:
            return

        errors = []

        for provider in (
            self.event_logger,
            self.tracing,
            self.metrics,
        ):
            try:
                provider.close()
            except Exception as exc:
                errors.append(exc)

        self._connected = False
        self._closed = True

        if errors:
            raise RuntimeError(
                f"Failed to close {len(errors)} monitoring provider(s)."
            ) from errors[0]

    def __enter__(self) -> ApplicationMonitor:
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()
