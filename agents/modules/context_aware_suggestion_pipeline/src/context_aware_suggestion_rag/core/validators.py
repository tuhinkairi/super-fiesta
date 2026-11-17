"""
Reusable validation utilities for Context-Aware Suggestion RAG.

Provides validation functions for identifiers, text, URLs,
metadata, and common pipeline inputs.
"""

import math
import re
from collections.abc import Mapping
from urllib.parse import urlparse

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.constants import (
    SUPPORTED_DOCUMENT_EXTENSIONS,
)
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.exceptions import (
    DocumentValidationError,
)


# ---------------------------------------------------------
# Validation patterns
# ---------------------------------------------------------

IDENTIFIER_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]{0,127}$")

MAX_TEXT_LENGTH = 100_000
MAX_METADATA_FIELDS = 50
MAX_METADATA_VALUE_LENGTH = 10_000


# ---------------------------------------------------------
# Identifier validation
# ---------------------------------------------------------

def validate_identifier(
    value: str,
    field_name: str = "identifier",
) -> str:
    """Validate and return a normalized identifier."""

    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string.")

    normalized = value.strip()

    if not IDENTIFIER_PATTERN.fullmatch(normalized):
        raise ValueError(
            f"{field_name} must contain 1-128 characters "
            "and use only letters, numbers, underscores, or hyphens."
        )

    return normalized


# ---------------------------------------------------------
# Text validation
# ---------------------------------------------------------

def validate_text(
    value: str,
    field_name: str = "text",
    max_length: int = MAX_TEXT_LENGTH,
    allow_empty: bool = False,
) -> str:
    """Validate and normalize a text value."""

    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string.")

    normalized = value.strip()

    if not allow_empty and not normalized:
        raise ValueError(f"{field_name} cannot be empty.")

    if len(normalized) > max_length:
        raise ValueError(
            f"{field_name} exceeds the maximum length of "
            f"{max_length} characters."
        )

    return normalized


# ---------------------------------------------------------
# URL validation
# ---------------------------------------------------------

def validate_url(value: str) -> str:
    """Validate an HTTP or HTTPS URL."""

    normalized = validate_text(
        value,
        field_name="URL",
        max_length=2048,
    )

    parsed = urlparse(normalized)

    if parsed.scheme not in {"http", "https"}:
        raise ValueError("URL must use HTTP or HTTPS.")

    if not parsed.hostname:
        raise ValueError("URL must contain a valid hostname.")

    if parsed.username or parsed.password:
        raise ValueError("URLs containing credentials are not allowed.")

    return normalized


# ---------------------------------------------------------
# Document validation
# ---------------------------------------------------------

def validate_document_extension(filename: str) -> str:
    """Validate a document filename and return its extension."""

    normalized = validate_text(
        filename,
        field_name="filename",
        max_length=255,
    )

    if "/" in normalized or "\\" in normalized:
        raise DocumentValidationError(
            "Filename must not contain directory paths."
        )

    if normalized in {".", ".."}:
        raise DocumentValidationError("Invalid filename.")

    extension = "." + normalized.rsplit(".", 1)[-1].lower()

    if "." not in normalized or extension not in SUPPORTED_DOCUMENT_EXTENSIONS:
        raise DocumentValidationError(
            f"Unsupported document extension: {extension}"
        )

    return extension


def validate_document_content(content: str) -> str:
    """Validate document text content."""

    try:
        return validate_text(
            content,
            field_name="document content",
        )
    except ValueError as exc:
        raise DocumentValidationError(str(exc)) from exc


# ---------------------------------------------------------
# Numeric validation
# ---------------------------------------------------------

def validate_positive_number(
    value: int | float,
    field_name: str = "value",
) -> float:
    """Validate a positive finite numeric value."""

    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be a number.")

    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{field_name} must be a positive finite number.")

    return float(value)


def validate_non_negative_integer(
    value: int,
    field_name: str = "value",
) -> int:
    """Validate a non-negative integer."""

    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{field_name} must be an integer.")

    if value < 0:
        raise ValueError(f"{field_name} cannot be negative.")

    return value


# ---------------------------------------------------------
# Metadata validation
# ---------------------------------------------------------

def validate_metadata(
    metadata: Mapping[str, object],
) -> dict[str, str | int | float | bool | list[str]]:
    """
    Validate metadata before vector database storage.

    Only scalar JSON-compatible values and lists of strings
    are accepted by the current metadata contract.
    """

    if not isinstance(metadata, Mapping):
        raise ValueError("Metadata must be a mapping.")

    if len(metadata) > MAX_METADATA_FIELDS:
        raise ValueError(
            f"Metadata cannot contain more than {MAX_METADATA_FIELDS} fields."
        )

    validated: dict[str, str | int | float | bool | list[str]] = {}

    for key, value in metadata.items():
        if not isinstance(key, str) or not key.strip():
            raise ValueError("Metadata keys must be non-empty strings.")

        normalized_key = key.strip()

        if len(normalized_key) > 128:
            raise ValueError("Metadata keys cannot exceed 128 characters.")

        if isinstance(value, bool):
            validated[normalized_key] = value

        elif isinstance(value, str):
            if len(value) > MAX_METADATA_VALUE_LENGTH:
                raise ValueError(
                    f"Metadata value for '{normalized_key}' is too long."
                )
            validated[normalized_key] = value

        elif isinstance(value, int):
            validated[normalized_key] = value

        elif isinstance(value, float):
            if not math.isfinite(value):
                raise ValueError(
                    f"Metadata value for '{normalized_key}' must be finite."
                )
            validated[normalized_key] = value

        elif isinstance(value, list):
            if not all(isinstance(item, str) for item in value):
                raise ValueError(
                    f"Metadata list '{normalized_key}' must contain strings only."
                )

            if any(len(item) > MAX_METADATA_VALUE_LENGTH for item in value):
                raise ValueError(
                    f"Metadata list '{normalized_key}' contains an oversized value."
                )

            validated[normalized_key] = value.copy()

        else:
            raise ValueError(
                f"Unsupported metadata value type for '{normalized_key}'."
            )

    return validated


# ---------------------------------------------------------
# Pipeline input validation
# ---------------------------------------------------------

def validate_query(query: str) -> str:
    """Validate a user search or recommendation query."""

    return validate_text(
        query,
        field_name="query",
        max_length=10_000,
    )


def validate_language(language: str) -> str:
    """Validate a language code."""

    normalized = validate_text(
        language,
        field_name="language",
        max_length=20,
    )

    if not re.fullmatch(r"[a-zA-Z]{2,3}(?:-[a-zA-Z0-9]{2,8})*", normalized):
        raise ValueError("Invalid language code.")

    return normalized.lower()


def validate_region(region: str) -> str:
    """Validate a two-letter region code."""

    normalized = validate_text(
        region,
        field_name="region",
        max_length=2,
    )

    if not re.fullmatch(r"[a-zA-Z]{2}", normalized):
        raise ValueError("Region must be a two-letter country code.")

    return normalized.upper()


__all__ = [
    "validate_identifier",
    "validate_text",
    "validate_url",
    "validate_document_extension",
    "validate_document_content",
    "validate_positive_number",
    "validate_non_negative_integer",
    "validate_metadata",
    "validate_query",
    "validate_language",
    "validate_region",
]
