"""
Centralized text-processing utilities.

Provides lightweight text normalization and cleanup functions
for document ingestion, embedding generation, and retrieval.
"""

import re
import unicodedata


WHITESPACE_PATTERN = re.compile(r"\s+")
MULTIPLE_NEWLINES_PATTERN = re.compile(r"\n{3,}")


def validate_string(value: str, field_name: str = "text") -> None:
    """Validate that a value is a string."""

    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")


def normalize_unicode(text: str) -> str:
    """
    Normalize Unicode characters using NFC normalization.

    This makes equivalent Unicode representations consistent
    without aggressively changing the original text.
    """

    validate_string(text)
    return unicodedata.normalize("NFC", text)


def remove_control_characters(
    text: str,
    *,
    preserve_newlines: bool = True,
    preserve_tabs: bool = True,
) -> str:
    """
    Remove unwanted Unicode control characters.

    Newlines and tabs can optionally be preserved.
    """

    validate_string(text)

    cleaned_characters: list[str] = []

    for character in text:
        if preserve_newlines and character == "\n":
            cleaned_characters.append(character)
            continue

        if preserve_tabs and character == "\t":
            cleaned_characters.append(character)
            continue

        if unicodedata.category(character) == "Cc":
            continue

        cleaned_characters.append(character)

    return "".join(cleaned_characters)


def normalize_whitespace(
    text: str,
    *,
    preserve_newlines: bool = False,
) -> str:
    """
    Normalize repeated whitespace.

    When preserve_newlines is True, line breaks are retained
    while excessive blank lines are reduced.
    """

    validate_string(text)

    if preserve_newlines:
        lines = [
            WHITESPACE_PATTERN.sub(" ", line).strip()
            for line in text.splitlines()
        ]

        normalized = "\n".join(lines)
        normalized = MULTIPLE_NEWLINES_PATTERN.sub("\n\n", normalized)

        return normalized.strip()

    return WHITESPACE_PATTERN.sub(" ", text).strip()


def normalize_text(
    text: str,
    *,
    preserve_newlines: bool = True,
) -> str:
    """
    Apply standard text cleanup operations.

    Operations:
    1. Unicode NFC normalization.
    2. Removal of unwanted control characters.
    3. Whitespace normalization.
    """

    validate_string(text)

    normalized = normalize_unicode(text)

    normalized = remove_control_characters(
        normalized,
        preserve_newlines=preserve_newlines,
        preserve_tabs=False,
    )

    return normalize_whitespace(
        normalized,
        preserve_newlines=preserve_newlines,
    )


def truncate_text(
    text: str,
    max_length: int,
    *,
    suffix: str = "...",
) -> str:
    """
    Truncate text to a maximum character length.

    The suffix is included within max_length.
    """

    validate_string(text)

    if isinstance(max_length, bool) or not isinstance(max_length, int):
        raise TypeError("max_length must be an integer")

    if max_length < 0:
        raise ValueError("max_length cannot be negative")

    validate_string(suffix, "suffix")

    if len(text) <= max_length:
        return text

    if max_length == 0:
        return ""

    if len(suffix) >= max_length:
        return suffix[:max_length]

    available_length = max_length - len(suffix)

    return text[:available_length] + suffix


def count_words(text: str) -> int:
    """Return the number of whitespace-separated words."""

    validate_string(text)

    return len(text.split())


def is_empty_text(text: str) -> bool:
    """Check whether text is empty or contains only whitespace."""

    validate_string(text)

    return not text.strip()


__all__ = [
    "validate_string",
    "normalize_unicode",
    "remove_control_characters",
    "normalize_whitespace",
    "normalize_text",
    "truncate_text",
    "count_words",
    "is_empty_text",
]
