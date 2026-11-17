
from context_aware_suggestion_rag.security.redaction import (
    SecretRedactor,
    redact_secrets,
)


def test_api_key_redaction():
    redactor = SecretRedactor()

    result = redactor.redact(
        "api_key=abcdefghijklmnopqrstuvwxyz123456"
    )

    assert "abcdefghijklmnopqrstuvwxyz123456" not in result.redacted_text
    assert "[REDACTED]" in result.redacted_text
    assert result.redactions_count == 1

    print("API key redaction: PASS")


def test_bearer_token_redaction():
    redactor = SecretRedactor()

    result = redactor.redact(
        "Authorization: Bearer abcdefghijklmnopqrstuvwxyz123456"
    )

    assert "abcdefghijklmnopqrstuvwxyz123456" not in result.redacted_text
    assert "[REDACTED]" in result.redacted_text

    print("Bearer token redaction: PASS")


def test_password_redaction():
    redactor = SecretRedactor()

    result = redactor.redact(
        "password=my_super_secret_password"
    )

    assert "my_super_secret_password" not in result.redacted_text
    assert "[REDACTED]" in result.redacted_text

    print("Password redaction: PASS")


def test_private_key_redaction():
    redactor = SecretRedactor()

    private_key = (
        "-----BEGIN RSA PRIVATE KEY-----\n"
        "PRIVATE_KEY_CONTENT\n"
        "-----END RSA PRIVATE KEY-----"
    )

    result = redactor.redact(private_key)

    assert "PRIVATE_KEY_CONTENT" not in result.redacted_text
    assert "[REDACTED]" in result.redacted_text

    print("Private key redaction: PASS")


def test_multiple_secrets():
    redactor = SecretRedactor()

    text = (
        "api_key=abcdefghijklmnopqrstuvwxyz123456 "
        "password=secret_password_123"
    )

    result = redactor.redact(text)

    assert result.redactions_count == 2
    assert "abcdefghijklmnopqrstuvwxyz123456" not in result.redacted_text
    assert "secret_password_123" not in result.redacted_text

    print("Multiple secret redaction: PASS")


def test_custom_replacement():
    redactor = SecretRedactor(replacement="<HIDDEN>")

    result = redactor.redact(
        "secret=my_secret_value"
    )

    assert "<HIDDEN>" in result.redacted_text

    print("Custom redaction replacement: PASS")


def test_redact_many():
    redactor = SecretRedactor()

    results = redactor.redact_many([
        "password=secret123",
        "api_key=abcdefghijklmnopqrstuvwxyz123456",
    ])

    assert len(results) == 2
    assert all(result.was_modified for result in results)

    print("Batch redaction: PASS")


def test_redact_mapping():
    redactor = SecretRedactor()

    data = {
        "message": "password=secret123",
        "details": {
            "token": "access_token=abcdefghijklmnopqrstuvwxyz123456",
        },
        "items": [
            "api_key=abcdefghijklmnopqrstuvwxyz123456",
            {"note": "password=another_secret"},
        ],
        "count": 10,
    }

    result = redactor.redact_mapping(data)

    assert "secret123" not in result["message"]
    assert "abcdefghijklmnopqrstuvwxyz123456" not in result["details"]["token"]
    assert "abcdefghijklmnopqrstuvwxyz123456" not in result["items"][0]
    assert "another_secret" not in result["items"][1]["note"]
    assert result["count"] == 10

    print("Nested mapping redaction: PASS")


def test_unchanged_text():
    redactor = SecretRedactor()

    result = redactor.redact("This is ordinary application text.")

    assert result.was_modified is False
    assert result.redactions_count == 0

    print("Unmodified text preservation: PASS")


def test_invalid_input():
    redactor = SecretRedactor()

    try:
        redactor.redact(123)
    except TypeError:
        pass
    else:
        raise AssertionError("Expected invalid input to raise TypeError.")

    print("Invalid input validation: PASS")


def test_convenience_function():
    result = redact_secrets("password=my_secret_password")

    assert "my_secret_password" not in result
    assert "[REDACTED]" in result

    print("Convenience redaction function: PASS")


if __name__ == "__main__":
    test_api_key_redaction()
    test_bearer_token_redaction()
    test_password_redaction()
    test_private_key_redaction()
    test_multiple_secrets()
    test_custom_replacement()
    test_redact_many()
    test_redact_mapping()
    test_unchanged_text()
    test_invalid_input()
    test_convenience_function()

    print("\nAll security redaction tests passed.")
