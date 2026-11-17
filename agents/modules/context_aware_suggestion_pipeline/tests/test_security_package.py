
from context_aware_suggestion_rag.security import (
    AccessControlManager,
    PasswordHasher,
    SecurityAuditLogger,
    SecurityInputValidator,
    SecurityMonitor,
    SecurityPolicyManager,
    SecurityService,
    SlidingWindowRateLimiter,
    TextSanitizer,
    create_security_service,
)


def test_security_package_imports():
    assert AccessControlManager is not None
    assert PasswordHasher is not None
    assert SecurityAuditLogger is not None
    assert SecurityInputValidator is not None
    assert SecurityMonitor is not None
    assert SecurityPolicyManager is not None
    assert SecurityService is not None
    assert SlidingWindowRateLimiter is not None
    assert TextSanitizer is not None
    assert callable(create_security_service)

    print("Security package imports: PASS")


def test_security_package_exports():
    import context_aware_suggestion_rag.security as security

    assert hasattr(security, "__all__")
    assert len(security.__all__) == len(set(security.__all__))

    for name in security.__all__:
        assert hasattr(security, name), f"Missing export: {name}"

    print(f"Security public exports ({len(security.__all__)}): PASS")


if __name__ == "__main__":
    test_security_package_imports()
    test_security_package_exports()

    print("All security package tests passed.")
