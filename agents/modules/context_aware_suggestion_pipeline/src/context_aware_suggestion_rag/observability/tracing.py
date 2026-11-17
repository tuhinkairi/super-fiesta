"""In-memory distributed tracing provider."""

from __future__ import annotations

from copy import deepcopy
from threading import RLock
from typing import Any
from uuid import uuid4

from .base import BaseTracingProvider
from .models import SpanStatus, TraceSpan, current_utc_time


class InMemoryTracingProvider(BaseTracingProvider):
    """Thread-safe in-memory tracing provider."""

    def __init__(self, max_spans: int = 10000) -> None:
        if (
            isinstance(max_spans, bool)
            or not isinstance(max_spans, int)
            or max_spans <= 0
        ):
            raise ValueError("max_spans must be a positive integer.")

        self.max_spans = max_spans
        self._spans: dict[str, TraceSpan] = {}
        self._trace_spans: dict[str, list[str]] = {}
        self._lock = RLock()
        self._connected = False
        self._closed = False

    def connect(self) -> None:
        """Initialize the tracing provider."""
        with self._lock:
            if self._closed:
                raise RuntimeError("Tracing provider is closed.")
            self._connected = True

    def health_check(self) -> bool:
        """Check whether the tracing provider is operational."""
        with self._lock:
            return self._connected and not self._closed

    def _ensure_connected(self) -> None:
        if self._closed:
            raise RuntimeError("Tracing provider is closed.")

        if not self._connected:
            self.connect()

    def start_span(
        self,
        name: str,
        parent_span_id: str | None = None,
        trace_id: str | None = None,
        attributes: dict[str, Any] | None = None,
    ) -> TraceSpan:
        """Create and register a new span."""
        self._ensure_connected()

        if not isinstance(name, str) or not name.strip():
            raise ValueError("Span name must be a non-empty string.")

        with self._lock:
            parent: TraceSpan | None = None

            if parent_span_id is not None:
                parent = self._spans.get(parent_span_id)

                if parent is None:
                    raise ValueError("Parent span does not exist.")

                if parent.ended_at is not None:
                    raise ValueError("Cannot create a child of an ended span.")

                if trace_id is not None and trace_id != parent.trace_id:
                    raise ValueError("Child span must use the parent's trace ID.")

                trace_id = parent.trace_id

            if trace_id is None:
                trace_id = uuid4().hex

            if not isinstance(trace_id, str) or not trace_id.strip():
                raise ValueError("Trace ID must be a non-empty string.")

            if attributes is not None and not isinstance(attributes, dict):
                raise TypeError("Span attributes must be a dictionary.")

            span = TraceSpan(
                name=name,
                trace_id=trace_id,
                span_id=uuid4().hex[:16],
                parent_span_id=parent_span_id,
                status=SpanStatus.UNSET,
                started_at=current_utc_time(),
                attributes=deepcopy(attributes or {}),
            )

            self._spans[span.span_id] = span
            self._trace_spans.setdefault(trace_id, []).append(span.span_id)

            self._enforce_limit()

            return deepcopy(span)

    def end_span(
        self,
        span_id: str,
        status: str = "ok",
        error: str | None = None,
    ) -> TraceSpan:
        """Finish an active span."""
        self._ensure_connected()

        if not isinstance(span_id, str) or not span_id.strip():
            raise ValueError("Span ID must be a non-empty string.")

        try:
            normalized_status = SpanStatus(status.lower())
        except (AttributeError, TypeError, ValueError) as exc:
            raise ValueError("Unsupported span status.") from exc

        if normalized_status == SpanStatus.UNSET:
            raise ValueError("An ended span must have OK or ERROR status.")

        if error is not None and not isinstance(error, str):
            raise TypeError("Span error must be a string or None.")

        with self._lock:
            span = self._spans.get(span_id)

            if span is None:
                raise KeyError(f"Span not found: {span_id}")

            if span.ended_at is not None:
                raise ValueError("Span has already ended.")

            span.ended_at = current_utc_time()
            span.status = normalized_status
            span.error = error

            if normalized_status == SpanStatus.ERROR and not error:
                span.error = "Span completed with an error."

            return deepcopy(span)

    def get_span(self, span_id: str) -> TraceSpan | None:
        """Retrieve a span by ID."""
        self._ensure_connected()

        with self._lock:
            span = self._spans.get(span_id)
            return deepcopy(span) if span is not None else None

    def get_trace(self, trace_id: str) -> list[TraceSpan]:
        """Retrieve all retained spans for a trace."""
        self._ensure_connected()

        if not isinstance(trace_id, str) or not trace_id.strip():
            raise ValueError("Trace ID must be a non-empty string.")

        with self._lock:
            span_ids = self._trace_spans.get(trace_id, [])
            return [
                deepcopy(self._spans[span_id])
                for span_id in span_ids
                if span_id in self._spans
            ]

    def add_event(
        self,
        span_id: str,
        name: str,
        attributes: dict[str, Any] | None = None,
    ) -> TraceSpan:
        """Attach an event to an active span."""
        self._ensure_connected()

        if not isinstance(name, str) or not name.strip():
            raise ValueError("Event name must be a non-empty string.")

        if attributes is not None and not isinstance(attributes, dict):
            raise TypeError("Event attributes must be a dictionary.")

        with self._lock:
            span = self._spans.get(span_id)

            if span is None:
                raise KeyError(f"Span not found: {span_id}")

            if span.ended_at is not None:
                raise ValueError("Cannot add an event to an ended span.")

            span.events.append(
                {
                    "name": name.strip(),
                    "timestamp": current_utc_time().isoformat(),
                    "attributes": deepcopy(attributes or {}),
                }
            )

            return deepcopy(span)

    def set_attribute(
        self,
        span_id: str,
        key: str,
        value: Any,
    ) -> TraceSpan:
        """Set an attribute on an active span."""
        self._ensure_connected()

        if not isinstance(key, str) or not key.strip():
            raise ValueError("Attribute key must be a non-empty string.")

        with self._lock:
            span = self._spans.get(span_id)

            if span is None:
                raise KeyError(f"Span not found: {span_id}")

            if span.ended_at is not None:
                raise ValueError("Cannot modify an ended span.")

            span.attributes[key.strip()] = deepcopy(value)
            return deepcopy(span)

    def get_active_spans(self) -> list[TraceSpan]:
        """Return all spans that have not ended."""
        self._ensure_connected()

        with self._lock:
            return [
                deepcopy(span)
                for span in self._spans.values()
                if span.ended_at is None
            ]

    def get_span_count(self) -> int:
        """Return the number of retained spans."""
        with self._lock:
            return len(self._spans)

    def _enforce_limit(self) -> None:
        """Remove oldest completed spans when the storage limit is exceeded."""
        while len(self._spans) > self.max_spans:
            removable_id = next(
                (
                    span_id
                    for span_id, span in self._spans.items()
                    if span.ended_at is not None
                ),
                None,
            )

            if removable_id is None:
                # Never silently discard active spans.
                self._spans.popitem()
                break

            removed = self._spans.pop(removable_id)

            trace_ids = self._trace_spans.get(removed.trace_id, [])
            if removable_id in trace_ids:
                trace_ids.remove(removable_id)

            if not trace_ids:
                self._trace_spans.pop(removed.trace_id, None)

    def clear(self) -> None:
        """Remove all stored spans."""
        self._ensure_connected()

        with self._lock:
            self._spans.clear()
            self._trace_spans.clear()

    def close(self) -> None:
        """Close the tracing provider."""
        with self._lock:
            self._connected = False
            self._closed = True
