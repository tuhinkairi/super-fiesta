"""
Security event monitoring.

Tracks security events, detects suspicious activity, and generates alerts.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from threading import RLock
from typing import Any

from context_aware_suggestion_rag.security.audit import SecurityAuditLogger
from context_aware_suggestion_rag.security.models import (
    SecurityAuditEvent,
    SecurityEventType,
    SecuritySeverity,
)


@dataclass(frozen=True, slots=True)
class SecurityAlert:
    """Represents a security monitoring alert."""

    message: str
    severity: SecuritySeverity
    event_id: str | None = None
    principal: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.message, str) or not self.message.strip():
            raise ValueError("Alert message cannot be empty.")

        if not isinstance(self.severity, SecuritySeverity):
            raise TypeError("severity must be a SecuritySeverity.")

        if self.metadata is None or not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary.")


@dataclass(frozen=True, slots=True)
class SecurityMonitorSnapshot:
    """Immutable snapshot of security monitoring statistics."""

    total_events: int
    events_by_severity: dict[str, int]
    events_by_type: dict[str, int]
    alerts_generated: int
    blocked_events: int


class SecurityMonitor:
    """Monitors security audit events and generates alerts."""

    def __init__(
        self,
        audit_logger: SecurityAuditLogger | None = None,
        alert_on_severity: SecuritySeverity = SecuritySeverity.HIGH,
    ) -> None:
        if not isinstance(alert_on_severity, SecuritySeverity):
            raise TypeError(
                "alert_on_severity must be a SecuritySeverity."
            )

        self.audit_logger = audit_logger or SecurityAuditLogger()
        self.alert_on_severity = alert_on_severity

        self._alerts: list[SecurityAlert] = []
        self._severity_counts: Counter[str] = Counter()
        self._type_counts: Counter[str] = Counter()
        self._blocked_events = 0
        self._lock = RLock()
        self._closed = False

    def _ensure_open(self) -> None:
        if self._closed:
            raise RuntimeError("SecurityMonitor is closed.")

    def process_event(
        self,
        event: SecurityAuditEvent,
    ) -> SecurityAlert | None:
        """Record and evaluate a security event."""
        self._ensure_open()

        if not isinstance(event, SecurityAuditEvent):
            raise TypeError("event must be a SecurityAuditEvent.")

        with self._lock:
            severity = event.severity.value
            event_type = event.event_type.value

            self._severity_counts[severity] += 1
            self._type_counts[event_type] += 1

            if event.event_type == SecurityEventType.ACCESS_DENIED:
                self._blocked_events += 1

            severity_order = {
                SecuritySeverity.INFO: 0,
                SecuritySeverity.LOW: 1,
                SecuritySeverity.MEDIUM: 2,
                SecuritySeverity.HIGH: 3,
                SecuritySeverity.CRITICAL: 4,
            }

            if severity_order[event.severity] < severity_order[
                self.alert_on_severity
            ]:
                return None

            alert = SecurityAlert(
                message=event.message,
                severity=event.severity,
                event_id=event.event_id,
                principal=event.principal,
                metadata={
                    "event_type": event_type,
                    "action": event.action,
                    "resource": event.resource,
                },
            )

            self._alerts.append(alert)

            return alert


    def record_event(
        self,
        event_type: SecurityEventType,
        severity: SecuritySeverity,
        message: str,
        *,
        principal: str | None = None,
        action: str | None = None,
        resource: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> SecurityAlert | None:
        """Create an audit event and process it."""
        self._ensure_open()

        event = self.audit_logger.log(
            event_type,
            severity,
            message,
            principal=principal,
            action=action,
            resource=resource,
            metadata=metadata or {},
        )

        if not isinstance(event, SecurityAuditEvent):
            raise TypeError(
                "SecurityAuditLogger.log() must return a SecurityAuditEvent."
            )

        return self.process_event(event)

    def get_alerts(
        self,
        severity: SecuritySeverity | None = None,
    ) -> list[SecurityAlert]:
        """Return generated alerts, optionally filtered by severity."""
        self._ensure_open()

        if severity is not None and not isinstance(
            severity,
            SecuritySeverity,
        ):
            raise TypeError("severity must be a SecuritySeverity.")

        with self._lock:
            alerts = list(self._alerts)

            if severity is not None:
                alerts = [
                    alert
                    for alert in alerts
                    if alert.severity == severity
                ]

            return alerts

    def get_recent_events(self, limit: int = 20) -> list[SecurityAuditEvent]:
        """Return recent events from the audit logger."""
        self._ensure_open()

        if isinstance(limit, bool) or not isinstance(limit, int) or limit <= 0:
            raise ValueError("limit must be a positive integer.")

        return self.audit_logger.get_events(limit=limit)

    def get_snapshot(self) -> SecurityMonitorSnapshot:
        """Return current monitoring statistics."""
        self._ensure_open()

        with self._lock:
            return SecurityMonitorSnapshot(
                total_events=sum(self._severity_counts.values()),
                events_by_severity=dict(self._severity_counts),
                events_by_type=dict(self._type_counts),
                alerts_generated=len(self._alerts),
                blocked_events=self._blocked_events,
            )

    def clear_alerts(self) -> int:
        """Clear generated alerts and return the number removed."""
        self._ensure_open()

        with self._lock:
            count = len(self._alerts)
            self._alerts.clear()
            return count

    def health_check(self) -> bool:
        """Check whether the monitor is operational."""
        return not self._closed

    def close(self) -> None:
        """Close the monitor and release its in-memory state."""
        with self._lock:
            self._alerts.clear()
            self._severity_counts.clear()
            self._type_counts.clear()
            self._blocked_events = 0
            self._closed = True
