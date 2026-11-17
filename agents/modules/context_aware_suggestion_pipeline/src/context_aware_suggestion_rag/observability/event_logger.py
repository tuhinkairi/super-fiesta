"""In-memory structured observability event logger."""

from __future__ import annotations

from collections import deque
from copy import deepcopy
from threading import RLock
from typing import Any

from .base import BaseEventLogger
from .models import ObservabilityEvent, current_utc_time


class InMemoryEventLogger(BaseEventLogger):
    """Thread-safe structured event logger."""

    VALID_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

    def __init__(self, max_events: int = 10000) -> None:
        if (
            isinstance(max_events, bool)
            or not isinstance(max_events, int)
            or max_events <= 0
        ):
            raise ValueError("max_events must be a positive integer.")

        self.max_events = max_events
        self._events: deque[ObservabilityEvent] = deque(maxlen=max_events)
        self._lock = RLock()
        self._connected = False
        self._closed = False

    def connect(self) -> None:
        """Initialize the event logger."""
        with self._lock:
            if self._closed:
                raise RuntimeError("Event logger is closed.")
            self._connected = True

    def health_check(self) -> bool:
        """Check whether the event logger is operational."""
        with self._lock:
            return self._connected and not self._closed

    def _ensure_connected(self) -> None:
        if self._closed:
            raise RuntimeError("Event logger is closed.")

        if not self._connected:
            self.connect()

    def log_event(
        self,
        name: str,
        message: str,
        level: str = "INFO",
        attributes: dict[str, Any] | None = None,
        trace_id: str | None = None,
        span_id: str | None = None,
    ) -> ObservabilityEvent:
        """Record a structured event."""
        self._ensure_connected()

        if not isinstance(level, str):
            raise TypeError("Event level must be a string.")

        normalized_level = level.upper()

        if normalized_level not in self.VALID_LEVELS:
            raise ValueError(
                f"Unsupported log level: {level}. "
                f"Expected one of {sorted(self.VALID_LEVELS)}."
            )

        if attributes is not None and not isinstance(attributes, dict):
            raise TypeError("Event attributes must be a dictionary.")

        event = ObservabilityEvent(
            name=name,
            message=message,
            level=normalized_level,
            timestamp=current_utc_time(),
            trace_id=trace_id,
            span_id=span_id,
            attributes=deepcopy(attributes or {}),
        )

        with self._lock:
            self._events.append(event)

        return deepcopy(event)

    def get_events(
        self,
        name: str | None = None,
        level: str | None = None,
        limit: int | None = None,
    ) -> list[ObservabilityEvent]:
        """Retrieve events with optional filters."""
        self._ensure_connected()

        if name is not None:
            if not isinstance(name, str) or not name.strip():
                raise ValueError("Event name filter must be non-empty.")
            name = name.strip()

        if level is not None:
            if not isinstance(level, str):
                raise TypeError("Level filter must be a string.")

            level = level.upper()

            if level not in self.VALID_LEVELS:
                raise ValueError("Unsupported level filter.")

        if limit is not None:
            if (
                isinstance(limit, bool)
                or not isinstance(limit, int)
                or limit <= 0
            ):
                raise ValueError("Limit must be a positive integer.")

        with self._lock:
            events = list(self._events)

        if name is not None:
            events = [event for event in events if event.name == name]

        if level is not None:
            events = [event for event in events if event.level == level]

        if limit is not None:
            events = events[-limit:]

        return deepcopy(events)

    def get_event(self, event_id: str) -> ObservabilityEvent | None:
        """Retrieve an event by its identifier."""
        self._ensure_connected()

        if not isinstance(event_id, str) or not event_id.strip():
            raise ValueError("Event ID must be a non-empty string.")

        with self._lock:
            for event in self._events:
                if event.event_id == event_id:
                    return deepcopy(event)

        return None

    def count(self, level: str | None = None) -> int:
        """Count events, optionally filtered by log level."""
        self._ensure_connected()

        if level is not None:
            if not isinstance(level, str):
                raise TypeError("Level must be a string.")

            level = level.upper()

            if level not in self.VALID_LEVELS:
                raise ValueError("Unsupported level.")

        with self._lock:
            if level is None:
                return len(self._events)

            return sum(event.level == level for event in self._events)

    def clear(self) -> None:
        """Remove all stored events."""
        self._ensure_connected()

        with self._lock:
            self._events.clear()

    def close(self) -> None:
        """Close the event logger."""
        with self._lock:
            self._connected = False
            self._closed = True
