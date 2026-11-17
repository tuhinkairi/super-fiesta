
from context_aware_suggestion_rag.interfaces.security_provider import (
    SecurityProvider,
    InputSanitizer,
    AccessControlProvider,
    SecurityValidator,
)


class FakeSanitizer(InputSanitizer):

    def sanitize(self, value):
        return value.strip()

    def health_check(self):
        return True


class FakeAccessControl(AccessControlProvider):

    def authorize(self, principal, action, resource, context=None):
        return principal == "admin"

    def health_check(self):
        return True


class FakeSecurityValidator(SecurityValidator):

    def validate(self, value, context=None):
        return isinstance(value, str) and bool(value.strip())

    def health_check(self):
        return True


def main():
    sanitizer = FakeSanitizer()
    access_control = FakeAccessControl()
    validator = FakeSecurityValidator()

    assert isinstance(sanitizer, SecurityProvider)
    assert isinstance(access_control, SecurityProvider)
    assert isinstance(validator, SecurityProvider)
    print("Security provider inheritance: PASS")

    assert sanitizer.health_check()
    assert access_control.health_check()
    assert validator.health_check()
    print("Security provider health checks: PASS")

    assert sanitizer.sanitize("  hello  ") == "hello"
    print("Input sanitization interface: PASS")

    assert access_control.authorize("admin", "read", "document")
    assert not access_control.authorize("guest", "delete", "document")
    print("Access control interface: PASS")

    assert validator.validate("valid input")
    assert not validator.validate("   ")
    print("Security validation interface: PASS")

    sanitizer.close()
    access_control.close()
    validator.close()
    print("Security provider close interface: PASS")

    print("\nAll security provider interface tests passed.")


if __name__ == "__main__":
    main()
