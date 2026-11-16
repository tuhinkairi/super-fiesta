"""
Central security service.

Coordinates sanitization, input validation, access control,
policy evaluation, and optional audit logging.
"""

from __future__ import annotations

from typing import Any

from context_aware_suggestion_rag.security.access_control import (
    AccessControlManager,
)
from context_aware_suggestion_rag.security.audit import (
    SecurityAuditLogger,
)
from context_aware_suggestion_rag.security.policies import (
    SecurityPolicyManager,
)
from context_aware_suggestion_rag.security.sanitizers import (
    TextSanitizer,
)
from context_aware_suggestion_rag.security.validators import (
    SecurityInputValidator,
)


class SecurityService:
    """High-level facade for the package security components."""

    def __init__(
        self,
        *,
        sanitizer: TextSanitizer | None = None,
        validator: SecurityInputValidator | None = None,
        access_control: AccessControlManager | None = None,
        policy_manager: SecurityPolicyManager | None = None,
        audit_logger: SecurityAuditLogger | None = None,
    ) -> None:
        self.sanitizer = sanitizer or TextSanitizer()
        self.validator = validator or SecurityInputValidator()
        self._closed = False
        self.access_control = (
            access_control or AccessControlManager()
        )
        self.policy_manager = (
            policy_manager or SecurityPolicyManager()
        )
        self.audit_logger = audit_logger or SecurityAuditLogger()

    def sanitize_input(self, value: str):
        """Sanitize untrusted text input."""
        if not isinstance(value, str):
            raise TypeError("Input value must be a string.")

        return self.sanitizer.sanitize(value)

    def validate_input(self, value: str):
        """Validate an input value without modifying it."""
        if not isinstance(value, str):
            raise TypeError("Input value must be a string.")

        return self.validator.validate(value)

    def process_input(self, value: str):
        """
        Sanitize input and validate the sanitized result.

        Returns:
            A tuple containing the sanitization and validation results.
        """
        sanitization_result = self.sanitize_input(value)

        validation_result = self.validate_input(
            sanitization_result.sanitized_value
        )

        return sanitization_result, validation_result

    def authorize(
        self,
        principal: str,
        action: Any,
        resource: str,
        context: dict[str, Any] | None = None,
    ):
        """Evaluate an access-control request."""
        return self.access_control.authorize(
            principal=principal,
            action=action,
            resource=resource,
            context=context,
        )

    def evaluate_policy(
        self,
        policy_name: str,
        value: Any,
        context: dict[str, Any] | None = None,
    ):
        """Evaluate a registered security policy."""
        if not isinstance(policy_name, str) or not policy_name.strip():
            raise ValueError("Policy name must be a non-empty string.")

        return self.policy_manager.evaluate(
            policy_name,
            value,
            context=context,
        )

    def get_audit_logger(self) -> SecurityAuditLogger:
        """Return the configured audit logger."""
        return self.audit_logger

    def health_check(self) -> dict[str, bool]:
        """Return the operational status of each security component."""
        if self._closed:
            return {
                "sanitizer": False,
                "validator": False,
                "access_control": False,
                "policy_manager": False,
            }

        return {
            "sanitizer": callable(
                getattr(self.sanitizer, "sanitize", None)
            ),
            "validator": callable(
                getattr(self.validator, "validate", None)
            ),
            "access_control": callable(
                getattr(self.access_control, "authorize", None)
            ),
            "policy_manager": callable(
                getattr(self.policy_manager, "evaluate", None)
            ),
        }

    def close(self) -> None:
        """Close components that expose a close method."""
        self._closed = True
        components = (
            self.sanitizer,
            self.validator,
            self.access_control,
            self.policy_manager,
            self.audit_logger,
        )

        for component in components:
            close = getattr(component, "close", None)

            if callable(close):
                close()


def create_security_service(
    *,
    sanitizer: TextSanitizer | None = None,
    validator: SecurityInputValidator | None = None,
    access_control: AccessControlManager | None = None,
    policy_manager: SecurityPolicyManager | None = None,
    audit_logger: SecurityAuditLogger | None = None,
) -> SecurityService:
    """Create a configured security service."""
    return SecurityService(
        sanitizer=sanitizer,
        validator=validator,
        access_control=access_control,
        policy_manager=policy_manager,
        audit_logger=audit_logger,
    )
