"""
Cryptographic utilities.

Provides secure password hashing, token generation, and HMAC operations.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PasswordHash:
    """Represents a PBKDF2 password hash."""

    algorithm: str
    iterations: int
    salt: str
    digest: str

    def __post_init__(self) -> None:
        if self.algorithm != "pbkdf2_sha256":
            raise ValueError("Unsupported password hashing algorithm.")

        if (
            isinstance(self.iterations, bool)
            or not isinstance(self.iterations, int)
            or self.iterations < 1
        ):
            raise ValueError("iterations must be a positive integer.")

        if not self.salt or not self.digest:
            raise ValueError("Salt and digest cannot be empty.")

    def encode(self) -> str:
        """Serialize the password hash."""
        return (
            f"{self.algorithm}${self.iterations}"
            f"${self.salt}${self.digest}"
        )

    @classmethod
    def decode(cls, encoded: str) -> PasswordHash:
        """Deserialize a password hash."""
        if not isinstance(encoded, str):
            raise TypeError("encoded must be a string.")

        parts = encoded.split("$")

        if len(parts) != 4:
            raise ValueError("Invalid encoded password hash.")

        algorithm, iterations, salt, digest = parts

        try:
            iteration_count = int(iterations)
        except ValueError as exc:
            raise ValueError("Invalid iteration count.") from exc

        return cls(
            algorithm=algorithm,
            iterations=iteration_count,
            salt=salt,
            digest=digest,
        )


class PasswordHasher:
    """Hashes and verifies passwords using PBKDF2-HMAC-SHA256."""

    ALGORITHM = "pbkdf2_sha256"
    DEFAULT_ITERATIONS = 600_000
    SALT_LENGTH = 16
    DIGEST_LENGTH = 32

    def __init__(self, iterations: int = DEFAULT_ITERATIONS) -> None:
        if (
            isinstance(iterations, bool)
            or not isinstance(iterations, int)
            or iterations < 1
        ):
            raise ValueError("iterations must be a positive integer.")

        self.iterations = iterations

    @staticmethod
    def _validate_password(password: str) -> None:
        if not isinstance(password, str):
            raise TypeError("password must be a string.")

        if not password:
            raise ValueError("password cannot be empty.")

    @staticmethod
    def _derive(
        password: str,
        salt: bytes,
        iterations: int,
    ) -> bytes:
        return hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            iterations,
            dklen=PasswordHasher.DIGEST_LENGTH,
        )

    def hash_password(self, password: str) -> str:
        """Generate a salted password hash."""
        self._validate_password(password)

        salt = secrets.token_bytes(self.SALT_LENGTH)

        digest = self._derive(
            password,
            salt,
            self.iterations,
        )

        encoded_salt = base64.urlsafe_b64encode(salt).decode("ascii")
        encoded_digest = base64.urlsafe_b64encode(digest).decode("ascii")

        return PasswordHash(
            algorithm=self.ALGORITHM,
            iterations=self.iterations,
            salt=encoded_salt,
            digest=encoded_digest,
        ).encode()

    def verify_password(
        self,
        password: str,
        encoded_hash: str,
    ) -> bool:
        """Verify a password against its encoded hash."""
        self._validate_password(password)

        try:
            stored = PasswordHash.decode(encoded_hash)

            salt = base64.b64decode(
                stored.salt,
                altchars=b"-_",
                validate=True,
            )

            expected_digest = base64.b64decode(
                stored.digest,
                altchars=b"-_",
                validate=True,
            )

            if (
                len(salt) != self.SALT_LENGTH
                or len(expected_digest) != self.DIGEST_LENGTH
            ):
                return False

            actual_digest = self._derive(
                password,
                salt,
                stored.iterations,
            )

            return hmac.compare_digest(
                actual_digest,
                expected_digest,
            )

        except (ValueError, TypeError, OverflowError):
            return False


def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure URL-safe token."""
    if (
        isinstance(length, bool)
        or not isinstance(length, int)
        or length < 16
    ):
        raise ValueError("Token length must be an integer of at least 16.")

    return secrets.token_urlsafe(length)


def hash_token(token: str) -> str:
    """Return the SHA-256 hexadecimal digest of a token."""
    if not isinstance(token, str):
        raise TypeError("token must be a string.")

    if not token:
        raise ValueError("token cannot be empty.")

    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def sign_message(message: str, secret_key: str) -> str:
    """Generate an HMAC-SHA256 signature for a message."""
    if not isinstance(message, str):
        raise TypeError("message must be a string.")

    if not isinstance(secret_key, str) or not secret_key:
        raise ValueError("secret_key must be a non-empty string.")

    signature = hmac.new(
        secret_key.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    )

    return signature.hexdigest()


def verify_signature(
    message: str,
    signature: str,
    secret_key: str,
) -> bool:
    """Verify an HMAC-SHA256 message signature."""
    if not isinstance(signature, str):
        return False

    try:
        expected = sign_message(message, secret_key)
    except (TypeError, ValueError):
        return False

    return hmac.compare_digest(expected, signature)
