
from context_aware_suggestion_rag.security.service import (
    SecurityService,
    create_security_service,
)


def test_service_creation():
    service = SecurityService()

    assert service.sanitizer is not None
    assert service.validator is not None
    assert service.access_control is not None
    assert service.policy_manager is not None
    assert service.audit_logger is not None

    print("Security service creation: PASS")


def test_factory():
    service = create_security_service()

    assert isinstance(service, SecurityService)

    print("Security service factory: PASS")


def test_sanitization():
    service = SecurityService()

    result = service.sanitize_input("Hello\x00World")

    assert result.sanitized_value == "HelloWorld"
    assert result.modified is True

    print("Input sanitization delegation: PASS")


def test_validation():
    service = SecurityService()

    result = service.validate_input("Valid input")

    assert result.valid is True

    print("Input validation delegation: PASS")


def test_process_input():
    service = SecurityService()

    sanitization, validation = service.process_input(
        "Hello\x00World"
    )

    assert sanitization.modified is True
    assert sanitization.sanitized_value == "HelloWorld"
    assert validation.valid is True

    print("Combined input processing: PASS")


def test_audit_logger_access():
    service = SecurityService()

    logger = service.get_audit_logger()

    assert logger is service.audit_logger

    print("Audit logger access: PASS")


def test_health_check():
    service = SecurityService()

    results = service.health_check()

    assert set(results) == {
        "sanitizer",
        "validator",
        "access_control",
        "policy_manager",
    }

    assert all(isinstance(value, bool) for value in results.values())

    print("Security component health check: PASS")


if __name__ == "__main__":
    test_service_creation()
    test_factory()
    test_sanitization()
    test_validation()
    test_process_input()
    test_audit_logger_access()
    test_health_check()

    print("\nAll security service tests passed.")
