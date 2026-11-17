
from context_aware_suggestion_rag.security.models import (
    AccessControlDecision,
    SanitizationResult,
    SecurityAction,
    SecurityAuditEvent,
    SecurityEventType,
    SecuritySeverity,
    SecurityValidationResult,
)


# Access control decision.
decision = AccessControlDecision(
    allowed=True,
    principal="user_123",
    action=SecurityAction.READ,
    resource="documents/123",
    reason="Authorized user.",
)

assert decision.allowed is True
assert decision.action == SecurityAction.READ

print("Access control decision: PASS")


# Validation result.
validation = SecurityValidationResult(
    valid=False,
    errors=["Invalid input detected."],
)

assert validation.valid is False
assert len(validation.errors) == 1

print("Security validation result: PASS")


# Sanitization result.
sanitization = SanitizationResult(
    original_value="<script>",
    sanitized_value="",
    modified=True,
    warnings=["Unsafe HTML removed."],
)

assert sanitization.modified is True
assert sanitization.has_warnings is True

print("Sanitization result: PASS")


# Audit event.
event = SecurityAuditEvent(
    event_type=SecurityEventType.ACCESS_DENIED,
    severity=SecuritySeverity.HIGH,
    message="Unauthorized document access.",
    principal="user_123",
    resource="documents/123",
)

assert event.event_id.startswith("sec_")
assert event.severity == SecuritySeverity.HIGH

print("Security audit event: PASS")


# Validation.
try:
    AccessControlDecision(
        allowed=True,
        principal="",
        action=SecurityAction.READ,
        resource="documents/123",
    )
    raise AssertionError("Invalid principal was accepted.")
except ValueError:
    pass

print("Security model validation: PASS")
print("All security model tests passed.")
