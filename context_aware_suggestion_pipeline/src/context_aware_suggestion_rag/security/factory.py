"""
Security component factories.

Provides centralized construction of security services and utilities.
"""

from __future__ import annotations

from context_aware_suggestion_rag.security.access_control import (
    AccessControlManager,
)
from context_aware_suggestion_rag.security.audit import SecurityAuditLogger
from context_aware_suggestion_rag.security.monitor import SecurityMonitor
from context_aware_suggestion_rag.security.policies import (
    SecurityPolicyManager,
)
from context_aware_suggestion_rag.security.rate_limiter import (
    RateLimitConfig,
    SlidingWindowRateLimiter,
)
from context_aware_suggestion_rag.security.redaction import SecretRedactor
from context_aware_suggestion_rag.security.sanitizers import (
    SanitizationConfig,
    TextSanitizer,
)
from context_aware_suggestion_rag.security.service import SecurityService
from context_aware_suggestion_rag.security.validators import (
    SecurityInputValidator,
    SecurityValidationConfig,
)
from context_aware_suggestion_rag.security.models import SecuritySeverity


def create_security_service(
    *,
    sanitizer: TextSanitizer | None = None,
    validator: SecurityInputValidator | None = None,
) -> SecurityService:
    """Create a security service."""
    return SecurityService(
        sanitizer=sanitizer,
        validator=validator,
    )


def create_text_sanitizer(
    config: SanitizationConfig | None = None,
) -> TextSanitizer:
    """Create a configured text sanitizer."""
    return TextSanitizer(config=config)


def create_input_validator(
    config: SecurityValidationConfig | None = None,
) -> SecurityInputValidator:
    """Create a configured input validator."""
    return SecurityInputValidator(config=config)


def create_access_control_manager() -> AccessControlManager:
    """Create an access-control manager."""
    return AccessControlManager()


def create_audit_logger() -> SecurityAuditLogger:
    """Create a security audit logger."""
    return SecurityAuditLogger()


def create_security_monitor(
    *,
    audit_logger: SecurityAuditLogger | None = None,
    alert_on_severity: SecuritySeverity = SecuritySeverity.HIGH,
) -> SecurityMonitor:
    """Create a security monitor."""
    return SecurityMonitor(
        audit_logger=audit_logger,
        alert_on_severity=alert_on_severity,
    )


def create_policy_manager() -> SecurityPolicyManager:
    """Create a security policy manager."""
    return SecurityPolicyManager()


def create_rate_limiter(
    config: RateLimitConfig | None = None,
) -> SlidingWindowRateLimiter:
    """Create a sliding-window rate limiter."""
    return SlidingWindowRateLimiter(config=config)


def create_secret_redactor(
    replacement: str = SecretRedactor.DEFAULT_REPLACEMENT,
) -> SecretRedactor:
    """Create a secret redactor."""
    return SecretRedactor(replacement=replacement)
