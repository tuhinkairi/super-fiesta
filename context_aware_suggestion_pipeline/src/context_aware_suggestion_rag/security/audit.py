"""
Security audit logging utilities.

Provides thread-safe in-memory audit event recording, filtering,
and export functionality.
"""

from __future__ import annotations

import json
from collections import deque
from datetime import datetime
from threading import RLock
from typing import Any, Iterable

from context_aware_suggestion_rag.security.models import (
    SecurityAction,
    SecurityAuditEvent,
    SecurityEventType,
    SecuritySeverity,
    current_utc_time,
)


class SecurityAuditLogger:
    """Thread-safe security audit event manager."""

    def __init__(self, max_events: int = 10_000) -> None:
        if (
            isinstance(max_events, bool)
            or not isinstance(max_events, int)
            or max_events <= 0
        ):
            raise ValueError("max_events must be a positive integer.")

        self.max_events = max_events
        self._events: deque[SecurityAuditEvent] = deque(
            maxlen=max_events
        )
        self._lock = RLock()

    # --------------------------------------------------------
    # Event Recording
    # --------------------------------------------------------

    def log(
        self,
        event_type: SecurityEventType | str,
        severity: SecuritySeverity | str,
        message: str,
        *,
        principal: str | None = None,
        action: SecurityAction | str | None = None,
        resource: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> SecurityAuditEvent:
        """Create and record a security audit event."""

        event = SecurityAuditEvent(
            event_type=event_type,
            severity=severity,
            message=message,
            principal=principal,
            action=action,
            resource=resource,
            metadata=dict(metadata or {}),
            timestamp=current_utc_time(),
        )

        with self._lock:
            self._events.append(event)

        return event

    def log_authorization(
        self,
        principal: str,
        action: SecurityAction | str,
        resource: str,
        allowed: bool,
        reason: str = "",
    ) -> SecurityAuditEvent:
        """Record an authorization decision."""

        if not isinstance(allowed, bool):
            raise TypeError("allowed must be a boolean.")

        return self.log(
            event_type=(
                SecurityEventType.AUTHORIZATION
                if allowed
                else SecurityEventType.ACCESS_DENIED
            ),
            severity=(
                SecuritySeverity.INFO
                if allowed
                else SecuritySeverity.WARNING
                if hasattr(SecuritySeverity, "WARNING")
                else SecuritySeverity.HIGH
            ),
            message=reason or (
                "Access granted."
                if allowed
                else "Access denied."
            ),
            principal=principal,
            action=action,
            resource=resource,
            metadata={"allowed": allowed},
        )

    def log_validation(
        self,
        message: str,
        *,
        principal: str | None = None,
        valid: bool,
        metadata: dict[str, Any] | None = None,
    ) -> SecurityAuditEvent:
        """Record an input validation result."""

        return self.log(
            event_type=SecurityEventType.VALIDATION,
            severity=(
                SecuritySeverity.INFO
                if valid
                else SecuritySeverity.MEDIUM
            ),
            message=message,
            principal=principal,
            metadata={
                **(metadata or {}),
                "valid": valid,
            },
        )

    def log_sanitization(
        self,
        message: str,
        *,
        principal: str | None = None,
        modified: bool,
        metadata: dict[str, Any] | None = None,
    ) -> SecurityAuditEvent:
        """Record an input sanitization result."""

        return self.log(
            event_type=SecurityEventType.SANITIZATION,
            severity=(
                SecuritySeverity.INFO
                if not modified
                else SecuritySeverity.LOW
            ),
            message=message,
            principal=principal,
            metadata={
                **(metadata or {}),
                "modified": modified,
            },
        )

    # --------------------------------------------------------
    # Event Retrieval
    # --------------------------------------------------------

    def get_events(self) -> list[SecurityAuditEvent]:
        """Return a snapshot of all recorded events."""
        with self._lock:
            return list(self._events)

    def get_event(self, event_id: str) -> SecurityAuditEvent | None:
        """Retrieve an event by its identifier."""
        if not isinstance(event_id, str):
            raise TypeError("event_id must be a string.")

        with self._lock:
            return next(
                (
                    event
                    for event in self._events
                    if event.event_id == event_id
                ),
                None,
            )

    def filter_events(
        self,
        *,
        event_type: SecurityEventType | str | None = None,
        severity: SecuritySeverity | str | None = None,
        principal: str | None = None,
        action: SecurityAction | str | None = None,
        resource: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        limit: int | None = None,
    ) -> list[SecurityAuditEvent]:
        """Return events matching all supplied filters."""

        if limit is not None and (
            isinstance(limit, bool)
            or not isinstance(limit, int)
            or limit <= 0
        ):
            raise ValueError("limit must be a positive integer or None.")

        if start_time is not None:
            self._validate_datetime(start_time, "start_time")

        if end_time is not None:
            self._validate_datetime(end_time, "end_time")

        if (
            start_time is not None
            and end_time is not None
            and start_time > end_time
        ):
            raise ValueError("start_time cannot be later than end_time.")

        event_type = self._normalize_enum(
            event_type, SecurityEventType
        )
        severity = self._normalize_enum(
            severity, SecuritySeverity
        )
        action = self._normalize_enum(action, SecurityAction)

        with self._lock:
            events = list(self._events)

        matched = [
            event
            for event in events
            if (
                (event_type is None or event.event_type == event_type)
                and (severity is None or event.severity == severity)
                and (principal is None or event.principal == principal)
                and (action is None or event.action == action)
                and (resource is None or event.resource == resource)
                and (
                    start_time is None
                    or event.timestamp >= start_time
                )
                and (
                    end_time is None
                    or event.timestamp <= end_time
                )
            )
        ]

        matched.sort(
            key=lambda event: event.timestamp,
            reverse=True,
        )

        return matched[:limit] if limit is not None else matched

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    def count(self) -> int:
        """Return the number of retained audit events."""
        with self._lock:
            return len(self._events)

    def count_by_severity(self) -> dict[str, int]:
        """Return retained event counts grouped by severity."""
        counts = {severity.value: 0 for severity in SecuritySeverity}

        with self._lock:
            for event in self._events:
                counts[event.severity.value] += 1

        return counts

    def count_by_event_type(self) -> dict[str, int]:
        """Return retained event counts grouped by event type."""
        counts = {
            event_type.value: 0
            for event_type in SecurityEventType
        }

        with self._lock:
            for event in self._events:
                counts[event.event_type.value] += 1

        return counts

    # --------------------------------------------------------
    # Export
    # --------------------------------------------------------

    def export_events(
        self,
        events: Iterable[SecurityAuditEvent] | None = None,
        *,
        indent: int | None = 2,
    ) -> str:
        """Export audit events as JSON."""

        selected = (
            list(events)
            if events is not None
            else self.get_events()
        )

        for event in selected:
            if not isinstance(event, SecurityAuditEvent):
                raise TypeError(
                    "All exported items must be SecurityAuditEvent objects."
                )

        payload = [
            {
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "severity": event.severity.value,
                "message": event.message,
                "principal": event.principal,
                "action": (
                    event.action.value
                    if event.action is not None
                    else None
                ),
                "resource": event.resource,
                "timestamp": event.timestamp.isoformat(),
                "metadata": event.metadata,
            }
            for event in selected
        ]

        return json.dumps(
            payload,
            indent=indent,
            ensure_ascii=False,
            default=str,
        )

    # --------------------------------------------------------
    # Maintenance
    # --------------------------------------------------------

    def clear(self) -> int:
        """Remove all retained events and return the removed count."""
        with self._lock:
            removed = len(self._events)
            self._events.clear()
            return removed

    # --------------------------------------------------------
    # Internal Helpers
    # --------------------------------------------------------

    @staticmethod
    def _normalize_enum(
        value: Any,
        enum_type: type,
    ) -> Any:
        if value is None:
            return None

        if isinstance(value, enum_type):
            return value

        if isinstance(value, str):
            try:
                return enum_type(value.lower())
            except ValueError:
                raise ValueError(
                    f"Unsupported {enum_type.__name__}: {value!r}"
                ) from None

        raise TypeError(
            f"Expected {enum_type.__name__}, string, or None."
        )

    @staticmethod
    def _validate_datetime(
        value: datetime,
        field_name: str,
    ) -> None:
        if not isinstance(value, datetime):
            raise TypeError(f"{field_name} must be a datetime.")

        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError(
                f"{field_name} must be timezone-aware."
            )
