
from context_aware_suggestion_rag.utils.security_utils import (
    constant_time_compare,
    generate_secure_password,
    generate_secure_token,
    hmac_sha256,
    mask_email,
    mask_string,
    redact_mapping,
    sha256_hash,
    sha512_hash,
)


def test_generate_secure_token():
    token = generate_secure_token(32)

    assert len(token) == 32
    assert all(char in "0123456789abcdef" for char in token)


def test_generate_secure_password():
    password = generate_secure_password(16)

    assert len(password) == 16
    assert any(char.isupper() for char in password)
    assert any(char.islower() for char in password)
    assert any(char.isdigit() for char in password)


def test_generate_password_without_symbols():
    password = generate_secure_password(
        12,
        include_symbols=False,
    )

    assert len(password) == 12
    assert all(char.isalnum() for char in password)


def test_sha256_hash():
    assert sha256_hash("hello") == (
        "2cf24dba5fb0a30e26e83b2ac5b9e29e"
        "1b161e5c1fa7425e73043362938b9824"
    )


def test_sha512_hash():
    result = sha512_hash("hello")
    assert len(result) == 128


def test_hmac_sha256():
    result = hmac_sha256("message", "secret")
    assert len(result) == 64


def test_constant_time_compare():
    assert constant_time_compare("token", "token") is True
    assert constant_time_compare("token", "other") is False


def test_mask_string():
    assert mask_string("1234567890") == "12******90"
    assert mask_string("abcdef", visible_start=1, visible_end=1) == "a****f"


def test_mask_email():
    assert mask_email("rohan@example.com") == "r***n@example.com"


def test_redact_mapping():
    data = {
        "username": "user",
        "password": "secret123",
        "settings": {
            "api_key": "private-key",
            "theme": "dark",
        },
    }

    result = redact_mapping(data)

    assert result["username"] == "user"
    assert result["password"] == "[REDACTED]"
    assert result["settings"]["api_key"] == "[REDACTED]"
    assert result["settings"]["theme"] == "dark"

    # Original data must remain unchanged.
    assert data["password"] == "secret123"


if __name__ == "__main__":
    tests = [
        test_generate_secure_token,
        test_generate_secure_password,
        test_generate_password_without_symbols,
        test_sha256_hash,
        test_sha512_hash,
        test_hmac_sha256,
        test_constant_time_compare,
        test_mask_string,
        test_mask_email,
        test_redact_mapping,
    ]

    for test in tests:
        test()
        print(f"{test.__name__}: PASS")

    print("All security utility tests passed.")
