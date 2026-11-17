"""General-purpose security utility functions."""

import hashlib
import hmac
import secrets
import string
from typing import Any


def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure hexadecimal token."""
    if isinstance(length, bool) or not isinstance(length, int):
        raise TypeError("length must be an integer")

    if length <= 0:
        raise ValueError("length must be greater than zero")

    return secrets.token_hex((length + 1) // 2)[:length]


def generate_secure_password(
    length: int = 16,
    *,
    include_uppercase: bool = True,
    include_lowercase: bool = True,
    include_digits: bool = True,
    include_symbols: bool = True,
) -> str:
    """Generate a cryptographically secure random password."""
    if isinstance(length, bool) or not isinstance(length, int):
        raise TypeError("length must be an integer")

    if length <= 0:
        raise ValueError("length must be greater than zero")

    character_groups = []

    if include_uppercase:
        character_groups.append(string.ascii_uppercase)

    if include_lowercase:
        character_groups.append(string.ascii_lowercase)

    if include_digits:
        character_groups.append(string.digits)

    if include_symbols:
        character_groups.append("!@#$%^&*()-_=+[]{}?")

    if not character_groups:
        raise ValueError("At least one character group must be enabled")

    if length < len(character_groups):
        raise ValueError(
            "length must allow at least one character from each enabled group"
        )

    password = [
        secrets.choice(group)
        for group in character_groups
    ]

    alphabet = "".join(character_groups)

    password.extend(
        secrets.choice(alphabet)
        for _ in range(length - len(password))
    )

    secrets.SystemRandom().shuffle(password)

    return "".join(password)


def sha256_hash(value: str | bytes) -> str:
    """Return the SHA-256 hexadecimal digest of a value."""
    if not isinstance(value, (str, bytes)):
        raise TypeError("value must be a string or bytes")

    data = value.encode("utf-8") if isinstance(value, str) else value

    return hashlib.sha256(data).hexdigest()


def sha512_hash(value: str | bytes) -> str:
    """Return the SHA-512 hexadecimal digest of a value."""
    if not isinstance(value, (str, bytes)):
        raise TypeError("value must be a string or bytes")

    data = value.encode("utf-8") if isinstance(value, str) else value

    return hashlib.sha512(data).hexdigest()


def hmac_sha256(
    message: str | bytes,
    secret_key: str | bytes,
) -> str:
    """Create an HMAC-SHA256 authentication digest."""
    if not isinstance(message, (str, bytes)):
        raise TypeError("message must be a string or bytes")

    if not isinstance(secret_key, (str, bytes)):
        raise TypeError("secret_key must be a string or bytes")

    message_bytes = (
        message.encode("utf-8")
        if isinstance(message, str)
        else message
    )

    key_bytes = (
        secret_key.encode("utf-8")
        if isinstance(secret_key, str)
        else secret_key
    )

    return hmac.new(
        key_bytes,
        message_bytes,
        hashlib.sha256,
    ).hexdigest()


def constant_time_compare(
    first: str | bytes,
    second: str | bytes,
) -> bool:
    """Compare two values without ordinary content-dependent comparison."""
    if not isinstance(first, (str, bytes)):
        raise TypeError("first must be a string or bytes")

    if not isinstance(second, (str, bytes)):
        raise TypeError("second must be a string or bytes")

    first_bytes = first.encode("utf-8") if isinstance(first, str) else first
    second_bytes = second.encode("utf-8") if isinstance(second, str) else second

    return hmac.compare_digest(first_bytes, second_bytes)


def mask_string(
    value: str,
    *,
    visible_start: int = 2,
    visible_end: int = 2,
    mask_character: str = "*",
) -> str:
    """Mask the middle portion of a string."""
    if not isinstance(value, str):
        raise TypeError("value must be a string")

    if isinstance(visible_start, bool) or not isinstance(visible_start, int):
        raise TypeError("visible_start must be an integer")

    if isinstance(visible_end, bool) or not isinstance(visible_end, int):
        raise TypeError("visible_end must be an integer")

    if visible_start < 0 or visible_end < 0:
        raise ValueError("visible character counts cannot be negative")

    if not isinstance(mask_character, str) or len(mask_character) != 1:
        raise ValueError("mask_character must be exactly one character")

    if not value:
        return ""

    if visible_start + visible_end >= len(value):
        return mask_character * len(value)

    hidden_length = len(value) - visible_start - visible_end

    return (
        value[:visible_start]
        + mask_character * hidden_length
        + value[-visible_end:]
        if visible_end
        else value[:visible_start] + mask_character * hidden_length
    )


def mask_email(email: str) -> str:
    """Mask the local part of an email address."""
    if not isinstance(email, str):
        raise TypeError("email must be a string")

    if email.count("@") != 1:
        raise ValueError("Invalid email structure")

    local_part, domain = email.split("@", 1)

    if not local_part or not domain:
        raise ValueError("Email local part and domain cannot be empty")

    if len(local_part) <= 2:
        masked_local = "*" * len(local_part)
    else:
        masked_local = (
            local_part[0]
            + "*" * (len(local_part) - 2)
            + local_part[-1]
        )

    return f"{masked_local}@{domain}"


def redact_mapping(
    data: dict[str, Any],
    sensitive_keys: tuple[str, ...] = (
        "password",
        "token",
        "api_key",
        "secret",
        "authorization",
    ),
    replacement: str = "[REDACTED]",
) -> dict[str, Any]:
    """Redact values associated with sensitive dictionary keys."""
    if not isinstance(data, dict):
        raise TypeError("data must be a dictionary")

    if not isinstance(replacement, str):
        raise TypeError("replacement must be a string")

    normalized_keys = {
        key.casefold()
        for key in sensitive_keys
        if isinstance(key, str)
    }

    result: dict[str, Any] = {}

    for key, value in data.items():
        if isinstance(key, str) and key.casefold() in normalized_keys:
            result[key] = replacement
        elif isinstance(value, dict):
            result[key] = redact_mapping(
                value,
                sensitive_keys=sensitive_keys,
                replacement=replacement,
            )
        else:
            result[key] = value

    return result
