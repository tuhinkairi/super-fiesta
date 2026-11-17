
from context_aware_suggestion_rag.security.crypto import (
    PasswordHash,
    PasswordHasher,
    generate_secure_token,
    hash_token,
    sign_message,
    verify_signature,
)


def test_password_hashing():
    hasher = PasswordHasher(iterations=1000)

    encoded = hasher.hash_password("StrongPassword123!")

    assert isinstance(encoded, str)
    assert "pbkdf2_sha256" in encoded
    assert encoded != "StrongPassword123!"

    print("Password hashing: PASS")


def test_password_verification():
    hasher = PasswordHasher(iterations=1000)

    encoded = hasher.hash_password("StrongPassword123!")

    assert hasher.verify_password(
        "StrongPassword123!",
        encoded,
    ) is True

    assert hasher.verify_password(
        "WrongPassword123!",
        encoded,
    ) is False

    print("Password verification: PASS")


def test_unique_password_salts():
    hasher = PasswordHasher(iterations=1000)

    first = hasher.hash_password("SamePassword123!")
    second = hasher.hash_password("SamePassword123!")

    assert first != second

    print("Unique password salts: PASS")


def test_password_hash_serialization():
    original = PasswordHash(
        algorithm="pbkdf2_sha256",
        iterations=1000,
        salt="c2FsdA==",
        digest="ZGlnZXN0",
    )

    decoded = PasswordHash.decode(original.encode())

    assert decoded == original

    print("Password hash serialization: PASS")


def test_secure_token_generation():
    first = generate_secure_token()
    second = generate_secure_token()

    assert isinstance(first, str)
    assert len(first) >= 16
    assert first != second

    print("Secure token generation: PASS")


def test_token_hashing():
    token = "example_secure_token"

    first = hash_token(token)
    second = hash_token(token)

    assert first == second
    assert len(first) == 64
    assert first != token

    print("Token hashing: PASS")


def test_message_signing():
    message = "Important application message"
    secret = "example-signing-secret"

    signature = sign_message(message, secret)

    assert isinstance(signature, str)
    assert len(signature) == 64

    print("HMAC message signing: PASS")


def test_signature_verification():
    message = "Important application message"
    secret = "example-signing-secret"

    signature = sign_message(message, secret)

    assert verify_signature(message, signature, secret) is True

    assert verify_signature(
        "Modified message",
        signature,
        secret,
    ) is False

    assert verify_signature(
        message,
        signature,
        "wrong-secret",
    ) is False

    print("HMAC signature verification: PASS")


def test_invalid_inputs():
    hasher = PasswordHasher(iterations=1000)

    try:
        hasher.hash_password("")
    except ValueError:
        pass
    else:
        raise AssertionError("Expected empty password rejection.")

    try:
        generate_secure_token(8)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected short token rejection.")

    print("Cryptographic input validation: PASS")


if __name__ == "__main__":
    test_password_hashing()
    test_password_verification()
    test_unique_password_salts()
    test_password_hash_serialization()
    test_secure_token_generation()
    test_token_hashing()
    test_message_signing()
    test_signature_verification()
    test_invalid_inputs()

    print("\nAll security cryptography tests passed.")
