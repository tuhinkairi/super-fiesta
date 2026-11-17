"""
Security-related models and data structures.

Defines common enums and dataclasses used by the security package.
"""

from __future__ import annotations
from uuid import uuid4
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


# ============================================================
# Utilities
# ============================================================

def current_utc_time() -> datetime:
    """Return the current timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


def _validate_aware_datetime(value: datetime, field_name: str) -> None:
    """Ensure a datetime is timezone-aware."""
    if not isinstance(value, datetime):
        raise TypeError(f"{field_name} must be a datetime.")

    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware.")


# ============================================================
# Enums
# ============================================================

class SecurityAction(str, Enum):
    """Actions that can be evaluated by security controls."""

    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXECUTE = "execute"
    ADMIN = "admin"


class SecuritySeverity(str, Enum):
    """Severity levels for security events."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityEventType(str, Enum):
    """Categories of security-related events."""

    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    SANITIZATION = "sanitization"
    ACCESS_DENIED = "access_denied"
    CONFIGURATION = "configuration"
    SYSTEM = "system"


# ============================================================
# Access Control Models
# ============================================================

@dataclass(slots=True)
class AccessControlDecision:
    """Represents the result of an access-control evaluation."""

    allowed: bool
    principal: str
    action: SecurityAction | str
    resource: str
    reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    decided_at: datetime = field(default_factory=current_utc_time)

    def __post_init__(self) -> None:
        if not isinstance(self.allowed, bool):
            raise TypeError("allowed must be a boolean.")

        if not isinstance(self.principal, str) or not self.principal.strip():
            raise ValueError("principal must be a non-empty string.")

        if isinstance(self.action, str):
            try:
                self.action = SecurityAction(self.action.lower())
            except ValueError:
                raise ValueError(
                    f"Unsupported security action: {self.action!r}"
                ) from None

        if not isinstance(self.action, SecurityAction):
            raise TypeError("action must be a SecurityAction.")

        if not isinstance(self.resource, str) or not self.resource.strip():
            raise ValueError("resource must be a non-empty string.")

        if not isinstance(self.reason, str):
            raise TypeError("reason must be a string.")

        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary.")

        _validate_aware_datetime(self.decided_at, "decided_at")


# ============================================================
# Validation Models
# ============================================================

@dataclass(slots=True)
class SecurityValidationResult:
    """Represents the result of a security validation operation."""

    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.valid, bool):
            raise TypeError("valid must be a boolean.")

        if not isinstance(self.errors, list):
            raise TypeError("errors must be a list.")

        if not isinstance(self.warnings, list):
            raise TypeError("warnings must be a list.")

        if not all(isinstance(item, str) for item in self.errors):
            raise TypeError("All errors must be strings.")

        if not all(isinstance(item, str) for item in self.warnings):
            raise TypeError("All warnings must be strings.")

        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary.")

    @property
    def has_errors(self) -> bool:
        """Return whether validation produced errors."""
        return bool(self.errors)

    @property
    def has_warnings(self) -> bool:
        """Return whether validation produced warnings."""
        return bool(self.warnings)


# ============================================================
# Sanitization Models
# ============================================================

@dataclass(slots=True)
class SanitizationResult:
    """Represents the result of sanitizing an input value."""

    original_value: str
    sanitized_value: str
    modified: bool
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.original_value, str):
            raise TypeError("original_value must be a string.")

        if not isinstance(self.sanitized_value, str):
            raise TypeError("sanitized_value must be a string.")

        if not isinstance(self.modified, bool):
            raise TypeError("modified must be a boolean.")

        if not isinstance(self.warnings, list):
            raise TypeError("warnings must be a list.")

        if not all(isinstance(item, str) for item in self.warnings):
            raise TypeError("All warnings must be strings.")

        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary.")

        if self.modified != (self.original_value != self.sanitized_value):
            raise ValueError(
                "modified must accurately reflect whether the value changed."
            )

    @property
    def has_warnings(self) -> bool:
        """Return whether sanitization produced warnings."""
        return bool(self.warnings)


# ============================================================
# Security Audit Event
# ============================================================


@dataclass(slots=True)
class SecurityAuditEvent:
    """Represents a recorded security-related event."""

    event_type: SecurityEventType | str
    severity: SecuritySeverity | str
    message: str
    principal: str | None = None
    action: SecurityAction | str | None = None
    resource: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=current_utc_time)
    event_id: str = field(
        default_factory=lambda: f"sec_{uuid4().hex}"
    )

    def __post_init__(self) -> None:
        if isinstance(self.event_type, str):
            self.event_type = SecurityEventType(self.event_type.lower())

        if not isinstance(self.event_type, SecurityEventType):
            raise TypeError("event_type must be a SecurityEventType.")

        if isinstance(self.severity, str):
            self.severity = SecuritySeverity(self.severity.lower())

        if not isinstance(self.severity, SecuritySeverity):
            raise TypeError("severity must be a SecuritySeverity.")

        if not isinstance(self.message, str) or not self.message.strip():
            raise ValueError("message must be a non-empty string.")

        if self.principal is not None and not isinstance(self.principal, str):
            raise TypeError("principal must be a string or None.")

        if isinstance(self.action, str):
            self.action = SecurityAction(self.action.lower())

        if self.action is not None and not isinstance(
            self.action, SecurityAction
        ):
            raise TypeError("action must be a SecurityAction or None.")

        if self.resource is not None and not isinstance(self.resource, str):
            raise TypeError("resource must be a string or None.")

        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary.")

        if not isinstance(self.event_id, str) or not self.event_id.startswith("sec_"):
            raise ValueError("event_id must start with 'sec_'.")

        _validate_aware_datetime(self.timestamp, "timestamp")

    @property
    def is_critical(self) -> bool:
        return self.severity == SecuritySeverity.CRITICAL

    @property
    def is_high_severity(self) -> bool:
        return self.severity in {
            SecuritySeverity.HIGH,
            SecuritySeverity.CRITICAL,
        }
