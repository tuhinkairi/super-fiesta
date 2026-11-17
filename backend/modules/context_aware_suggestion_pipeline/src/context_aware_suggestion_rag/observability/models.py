"""Data models for application observability."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from math import isfinite
from typing import Any
from uuid import uuid4


def current_utc_time() -> datetime:
    """Return the current timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


class MetricType(str, Enum):
    """Supported metric types."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMING = "timing"


class SpanStatus(str, Enum):
    """Execution status of a tracing span."""

    UNSET = "unset"
    OK = "ok"
    ERROR = "error"


@dataclass(slots=True)
class MetricRecord:
    """Represents a recorded application metric."""

    name: str
    metric_type: MetricType
    value: float
    description: str = ""
    unit: str | None = None
    labels: dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=current_utc_time)

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Metric name must be a non-empty string.")

        self.name = self.name.strip()

        if not isinstance(self.metric_type, MetricType):
            try:
                self.metric_type = MetricType(self.metric_type)
            except (TypeError, ValueError) as exc:
                raise ValueError("Unsupported metric type.") from exc

        if isinstance(self.value, bool) or not isinstance(
            self.value, (int, float)
        ):
            raise TypeError("Metric value must be numeric.")

        self.value = float(self.value)

        if not isfinite(self.value):
            raise ValueError("Metric value must be finite.")

        if not isinstance(self.description, str):
            raise TypeError("Metric description must be a string.")

        if self.unit is not None and (
            not isinstance(self.unit, str) or not self.unit.strip()
        ):
            raise ValueError("Metric unit must be a non-empty string or None.")

        if self.unit is not None:
            self.unit = self.unit.strip()

        if not isinstance(self.labels, dict):
            raise TypeError("Metric labels must be a dictionary.")

        for key, value in self.labels.items():
            if not isinstance(key, str) or not key.strip():
                raise ValueError("Metric label keys must be non-empty strings.")
            if not isinstance(value, str):
                raise TypeError("Metric label values must be strings.")

        if not isinstance(self.timestamp, datetime):
            raise TypeError("Metric timestamp must be a datetime.")

        if self.timestamp.tzinfo is None or self.timestamp.utcoffset() is None:
            raise ValueError("Metric timestamp must be timezone-aware.")


@dataclass(slots=True)
class TraceSpan:
    """Represents one operation within a distributed trace."""

    name: str
    trace_id: str = field(default_factory=lambda: uuid4().hex)
    span_id: str = field(default_factory=lambda: uuid4().hex[:16])
    parent_span_id: str | None = None
    status: SpanStatus = SpanStatus.UNSET
    started_at: datetime = field(default_factory=current_utc_time)
    ended_at: datetime | None = None
    attributes: dict[str, Any] = field(default_factory=dict)
    events: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Span name must be a non-empty string.")

        self.name = self.name.strip()

        for field_name, value in (
            ("trace_id", self.trace_id),
            ("span_id", self.span_id),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string.")

        if self.parent_span_id is not None and (
            not isinstance(self.parent_span_id, str)
            or not self.parent_span_id.strip()
        ):
            raise ValueError("Parent span ID must be a non-empty string or None.")

        if not isinstance(self.status, SpanStatus):
            try:
                self.status = SpanStatus(self.status)
            except (TypeError, ValueError) as exc:
                raise ValueError("Unsupported span status.") from exc

        if not isinstance(self.started_at, datetime):
            raise TypeError("Span start time must be a datetime.")

        if self.started_at.tzinfo is None or self.started_at.utcoffset() is None:
            raise ValueError("Span start time must be timezone-aware.")

        if self.ended_at is not None:
            if not isinstance(self.ended_at, datetime):
                raise TypeError("Span end time must be a datetime.")

            if self.ended_at.tzinfo is None or self.ended_at.utcoffset() is None:
                raise ValueError("Span end time must be timezone-aware.")

            if self.ended_at < self.started_at:
                raise ValueError("Span end time cannot precede start time.")

        if not isinstance(self.attributes, dict):
            raise TypeError("Span attributes must be a dictionary.")

        if not isinstance(self.events, list):
            raise TypeError("Span events must be a list.")

        if self.error is not None and not isinstance(self.error, str):
            raise TypeError("Span error must be a string or None.")

    @property
    def duration_ms(self) -> float | None:
        """Return the span duration in milliseconds, if completed."""
        if self.ended_at is None:
            return None

        return (self.ended_at - self.started_at).total_seconds() * 1000

    @property
    def is_completed(self) -> bool:
        """Whether the span has ended."""
        return self.ended_at is not None


@dataclass(slots=True)
class ObservabilityEvent:
    """Represents a structured observability event."""

    name: str
    message: str
    level: str = "INFO"
    event_id: str = field(default_factory=lambda: f"evt_{uuid4().hex}")
    timestamp: datetime = field(default_factory=current_utc_time)
    trace_id: str | None = None
    span_id: str | None = None
    attributes: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Event name must be a non-empty string.")

        if not isinstance(self.message, str):
            raise TypeError("Event message must be a string.")

        self.name = self.name.strip()
        self.level = self.level.upper() if isinstance(self.level, str) else self.level

        if self.level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            raise ValueError("Unsupported event log level.")

        if not isinstance(self.event_id, str) or not self.event_id.strip():
            raise ValueError("Event ID must be a non-empty string.")

        if not isinstance(self.timestamp, datetime):
            raise TypeError("Event timestamp must be a datetime.")

        if self.timestamp.tzinfo is None or self.timestamp.utcoffset() is None:
            raise ValueError("Event timestamp must be timezone-aware.")

        if self.trace_id is not None and not isinstance(self.trace_id, str):
            raise TypeError("Trace ID must be a string or None.")

        if self.span_id is not None and not isinstance(self.span_id, str):
            raise TypeError("Span ID must be a string or None.")

        if not isinstance(self.attributes, dict):
            raise TypeError("Event attributes must be a dictionary.")
