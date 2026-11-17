
import json

from context_aware_suggestion_rag.security.audit import (
    SecurityAuditLogger,
)
from context_aware_suggestion_rag.security.models import (
    SecurityAction,
    SecurityEventType,
    SecuritySeverity,
)


logger = SecurityAuditLogger()

# General event logging
event = logger.log(
    event_type=SecurityEventType.AUTHENTICATION,
    severity=SecuritySeverity.INFO,
    message="User authenticated successfully.",
    principal="user_1",
)

assert event.event_id.startswith("sec_")
assert logger.count() == 1
print("Security event logging: PASS")

# Authorization logging
denied = logger.log_authorization(
    principal="user_2",
    action=SecurityAction.DELETE,
    resource="documents",
    allowed=False,
    reason="Insufficient permissions.",
)

assert denied.event_type == SecurityEventType.ACCESS_DENIED
assert denied.metadata["allowed"] is False
print("Authorization audit logging: PASS")

# Validation logging
validation = logger.log_validation(
    "Input validation failed.",
    principal="user_2",
    valid=False,
)

assert validation.event_type == SecurityEventType.VALIDATION
assert validation.severity == SecuritySeverity.MEDIUM
print("Validation audit logging: PASS")

# Sanitization logging
sanitization = logger.log_sanitization(
    "Input was sanitized.",
    modified=True,
)

assert sanitization.event_type == SecurityEventType.SANITIZATION
print("Sanitization audit logging: PASS")

# Event retrieval
retrieved = logger.get_event(event.event_id)

assert retrieved is event
assert len(logger.get_events()) == 4
print("Audit event retrieval: PASS")

# Filtering
filtered = logger.filter_events(
    severity=SecuritySeverity.INFO,
)

assert len(filtered) == 1
print("Severity filtering: PASS")

filtered = logger.filter_events(
    principal="user_2",
)

assert len(filtered) == 2
print("Principal filtering: PASS")

# Statistics
severity_counts = logger.count_by_severity()

assert severity_counts["info"] == 1
assert severity_counts["high"] == 1
assert severity_counts["medium"] == 1
assert severity_counts["low"] == 1

print("Audit statistics: PASS")

# JSON export
exported = logger.export_events()
parsed = json.loads(exported)

assert len(parsed) == 4
assert parsed[0]["event_id"].startswith("sec_")

print("Audit JSON export: PASS")

# Clear
removed = logger.clear()

assert removed == 4
assert logger.count() == 0

print("Audit log clearing: PASS")

# Bounded storage
bounded_logger = SecurityAuditLogger(max_events=2)

for index in range(3):
    bounded_logger.log(
        SecurityEventType.SYSTEM,
        SecuritySeverity.INFO,
        f"Event {index}",
    )

assert bounded_logger.count() == 2

print("Bounded audit storage: PASS")

print("All security audit tests passed.")
