
from context_aware_suggestion_rag.database import health
from context_aware_suggestion_rag.embeddings import service
from context_aware_suggestion_rag.security.access_control import (
    AccessControlManager,
)
from context_aware_suggestion_rag.security.audit import SecurityAuditLogger
from context_aware_suggestion_rag.security.factory import (
    create_access_control_manager,
    create_audit_logger,
    create_input_validator,
    create_policy_manager,
    create_rate_limiter,
    create_secret_redactor,
    create_security_monitor,
    create_security_service,
    create_text_sanitizer,
)
from context_aware_suggestion_rag.security.monitor import SecurityMonitor
from context_aware_suggestion_rag.security.policies import (
    SecurityPolicyManager,
)
from context_aware_suggestion_rag.security.rate_limiter import (
    SlidingWindowRateLimiter,
)
from context_aware_suggestion_rag.security.redaction import SecretRedactor
from context_aware_suggestion_rag.security.sanitizers import TextSanitizer
from context_aware_suggestion_rag.security.service import SecurityService
from context_aware_suggestion_rag.security.validators import (
    SecurityInputValidator,
)


def test_security_service_factory():
    service = create_security_service()

    assert isinstance(service, SecurityService)
    health = service.health_check()

    assert isinstance(health, dict)
    assert set(health) == {
        "sanitizer",
        "validator",
        "access_control",
        "policy_manager",
    }
    assert all(health.values())
    print("Security service factory: PASS")


def test_sanitizer_factory():
    sanitizer = create_text_sanitizer()

    assert isinstance(sanitizer, TextSanitizer)

    print("Text sanitizer factory: PASS")


def test_validator_factory():
    validator = create_input_validator()

    assert isinstance(validator, SecurityInputValidator)

    print("Input validator factory: PASS")


def test_access_control_factory():
    manager = create_access_control_manager()

    assert isinstance(manager, AccessControlManager)

    print("Access-control factory: PASS")


def test_audit_logger_factory():
    logger = create_audit_logger()

    assert isinstance(logger, SecurityAuditLogger)

    print("Audit logger factory: PASS")


def test_monitor_factory():
    monitor = create_security_monitor()

    assert isinstance(monitor, SecurityMonitor)
    assert monitor.health_check() is True

    print("Security monitor factory: PASS")


def test_policy_factory():
    manager = create_policy_manager()

    assert isinstance(manager, SecurityPolicyManager)

    print("Policy manager factory: PASS")


def test_rate_limiter_factory():
    limiter = create_rate_limiter()

    assert isinstance(limiter, SlidingWindowRateLimiter)
    assert limiter.health_check() is True

    print("Rate limiter factory: PASS")


def test_redactor_factory():
    redactor = create_secret_redactor()

    assert isinstance(redactor, SecretRedactor)

    print("Secret redactor factory: PASS")


def test_dependency_injection():
    sanitizer = create_text_sanitizer()
    validator = create_input_validator()

    service = create_security_service(
        sanitizer=sanitizer,
        validator=validator,
    )

    assert service.sanitizer is sanitizer
    assert service.validator is validator

    print("Security factory dependency injection: PASS")


def test_shared_audit_logger():
    logger = create_audit_logger()

    monitor = create_security_monitor(
        audit_logger=logger,
    )

    assert monitor.audit_logger is logger

    print("Shared audit logger injection: PASS")


if __name__ == "__main__":
    test_security_service_factory()
    test_sanitizer_factory()
    test_validator_factory()
    test_access_control_factory()
    test_audit_logger_factory()
    test_monitor_factory()
    test_policy_factory()
    test_rate_limiter_factory()
    test_redactor_factory()
    test_dependency_injection()
    test_shared_audit_logger()

    print("\nAll security factory tests passed.")
