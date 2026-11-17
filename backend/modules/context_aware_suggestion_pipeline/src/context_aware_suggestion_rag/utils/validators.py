"""General-purpose validation utilities."""

from __future__ import annotations

import math
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")


def validate_not_none(value: Any, field_name: str = "value") -> None:
    """Ensure that a value is not None."""
    if value is None:
        raise ValueError(f"{field_name} must not be None.")


def validate_non_empty_string(
    value: Any,
    field_name: str = "value",
) -> str:
    """Validate and return a non-empty string."""
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string.")

    normalized = value.strip()

    if not normalized:
        raise ValueError(f"{field_name} must not be empty.")

    return normalized


def validate_identifier(
    value: Any,
    field_name: str = "identifier",
) -> str:
    """Validate a safe identifier."""
    identifier = validate_non_empty_string(value, field_name)

    if not IDENTIFIER_PATTERN.fullmatch(identifier):
        raise ValueError(
            f"{field_name} contains invalid characters or exceeds 128 characters."
        )

    return identifier


def validate_positive_integer(
    value: Any,
    field_name: str = "value",
) -> int:
    """Validate a positive integer."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an integer.")

    if value <= 0:
        raise ValueError(f"{field_name} must be greater than zero.")

    return value


def validate_non_negative_integer(
    value: Any,
    field_name: str = "value",
) -> int:
    """Validate a non-negative integer."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an integer.")

    if value < 0:
        raise ValueError(f"{field_name} must not be negative.")

    return value


def validate_positive_number(
    value: Any,
    field_name: str = "value",
) -> float:
    """Validate a finite positive number."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be numeric.")

    number = float(value)

    if not math.isfinite(number) or number <= 0:
        raise ValueError(f"{field_name} must be finite and greater than zero.")

    return number


def validate_non_negative_number(
    value: Any,
    field_name: str = "value",
) -> float:
    """Validate a finite non-negative number."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be numeric.")

    number = float(value)

    if not math.isfinite(number) or number < 0:
        raise ValueError(f"{field_name} must be finite and non-negative.")

    return number


def validate_probability(
    value: Any,
    field_name: str = "probability",
) -> float:
    """Validate a number in the inclusive range [0, 1]."""
    number = validate_non_negative_number(value, field_name)

    if number > 1:
        raise ValueError(f"{field_name} must not exceed 1.")

    return number


def validate_url(value: Any, field_name: str = "url") -> str:
    """Validate an absolute HTTP or HTTPS URL."""
    url = validate_non_empty_string(value, field_name)

    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        port = parsed.port
    except ValueError as exc:
        raise ValueError(f"{field_name} is invalid.") from exc

    if parsed.scheme.lower() not in {"http", "https"}:
        raise ValueError(f"{field_name} must use HTTP or HTTPS.")

    if not hostname:
        raise ValueError(f"{field_name} must contain a hostname.")

    if port is not None and not 1 <= port <= 65535:
        raise ValueError(f"{field_name} contains an invalid port.")

    return url


def validate_path(
    value: Any,
    field_name: str = "path",
    *,
    must_exist: bool = False,
    must_be_file: bool = False,
    must_be_directory: bool = False,
) -> Path:
    """Validate a filesystem path and optional filesystem constraints."""
    if not isinstance(value, (str, Path)):
        raise TypeError(f"{field_name} must be a string or Path.")

    raw_path = str(value).strip()

    if not raw_path:
        raise ValueError(f"{field_name} must not be empty.")

    path = Path(raw_path).expanduser()

    if must_be_file and must_be_directory:
        raise ValueError("A path cannot be both a file and a directory.")

    if must_exist and not path.exists():
        raise FileNotFoundError(f"{field_name} does not exist: {path}")

    if must_be_file and not path.is_file():
        raise ValueError(f"{field_name} must point to a file.")

    if must_be_directory and not path.is_dir():
        raise ValueError(f"{field_name} must point to a directory.")

    return path


def validate_mapping(
    value: Any,
    field_name: str = "mapping",
) -> Mapping:
    """Validate that a value is a mapping."""
    if not isinstance(value, Mapping):
        raise TypeError(f"{field_name} must be a mapping.")

    return value


def validate_sequence(
    value: Any,
    field_name: str = "sequence",
    *,
    allow_empty: bool = True,
    item_type: type | tuple[type, ...] | None = None,
) -> Sequence:
    """Validate a sequence, excluding strings and byte sequences."""
    if not isinstance(value, Sequence) or isinstance(
        value,
        (str, bytes, bytearray),
    ):
        raise TypeError(f"{field_name} must be a sequence.")

    if not allow_empty and not value:
        raise ValueError(f"{field_name} must not be empty.")

    if item_type is not None:
        for index, item in enumerate(value):
            if not isinstance(item, item_type):
                raise TypeError(
                    f"{field_name}[{index}] has an invalid item type."
                )

    return value


def validate_choice(
    value: Any,
    choices: Sequence[Any],
    field_name: str = "value",
) -> Any:
    """Validate that a value belongs to an allowed collection."""
    if not choices:
        raise ValueError("choices must not be empty.")

    if value not in choices:
        raise ValueError(
            f"{field_name} must be one of: {', '.join(map(str, choices))}."
        )

    return value
