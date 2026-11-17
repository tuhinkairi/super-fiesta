"""Reusable regular-expression utilities."""

import re
from re import Pattern
from typing import Any


URL_PATTERN = re.compile(
    r"https?://[^\s<>\"']+",
    re.IGNORECASE,
)

EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

HASHTAG_PATTERN = re.compile(
    r"(?<!\w)#[A-Za-z0-9_]+"
)

MENTION_PATTERN = re.compile(
    r"(?<!\w)@[A-Za-z0-9_]+"
)

WORD_PATTERN = re.compile(
    r"\b[\w]+(?:['’-][\w]+)*\b",
    re.UNICODE,
)

WHITESPACE_PATTERN = re.compile(r"\s+")


def compile_pattern(
    pattern: str,
    flags: int = 0,
) -> Pattern[str]:
    """Compile a regular-expression pattern."""
    if not isinstance(pattern, str):
        raise TypeError("pattern must be a string")

    try:
        return re.compile(pattern, flags)
    except re.error as error:
        raise ValueError(f"Invalid regular expression: {error}") from error


def extract_urls(text: str) -> list[str]:
    """Extract URL-like strings from text."""
    _validate_text(text)
    return URL_PATTERN.findall(text)


def extract_emails(text: str) -> list[str]:
    """Extract email addresses from text."""
    _validate_text(text)
    return EMAIL_PATTERN.findall(text)


def extract_hashtags(text: str) -> list[str]:
    """Extract hashtags from text."""
    _validate_text(text)
    return HASHTAG_PATTERN.findall(text)


def extract_mentions(text: str) -> list[str]:
    """Extract @mentions from text."""
    _validate_text(text)
    return MENTION_PATTERN.findall(text)


def extract_words(text: str) -> list[str]:
    """Extract words while retaining internal apostrophes and hyphens."""
    _validate_text(text)
    return WORD_PATTERN.findall(text)


def find_all(
    pattern: str | Pattern[str],
    text: str,
    flags: int = 0,
) -> list[str]:
    """Find all matches of a regular expression."""
    _validate_text(text)

    compiled = (
        compile_pattern(pattern, flags)
        if isinstance(pattern, str)
        else pattern
    )

    if not hasattr(compiled, "findall"):
        raise TypeError("pattern must be a string or compiled regex")

    return compiled.findall(text)


def contains_pattern(
    pattern: str | Pattern[str],
    text: str,
    flags: int = 0,
) -> bool:
    """Check whether text contains a pattern."""
    _validate_text(text)

    compiled = (
        compile_pattern(pattern, flags)
        if isinstance(pattern, str)
        else pattern
    )

    return compiled.search(text) is not None


def replace_pattern(
    pattern: str | Pattern[str],
    replacement: str,
    text: str,
    *,
    flags: int = 0,
    count: int = 0,
) -> str:
    """Replace regex matches in text."""
    _validate_text(text)

    if not isinstance(replacement, str):
        raise TypeError("replacement must be a string")

    if isinstance(count, bool) or not isinstance(count, int):
        raise TypeError("count must be an integer")

    if count < 0:
        raise ValueError("count cannot be negative")

    compiled = (
        compile_pattern(pattern, flags)
        if isinstance(pattern, str)
        else pattern
    )

    return compiled.sub(replacement, text, count=count)


def split_by_pattern(
    pattern: str | Pattern[str],
    text: str,
    *,
    max_splits: int = 0,
    flags: int = 0,
) -> list[str]:
    """Split text using a regular expression."""
    _validate_text(text)

    if isinstance(max_splits, bool) or not isinstance(max_splits, int):
        raise TypeError("max_splits must be an integer")

    if max_splits < 0:
        raise ValueError("max_splits cannot be negative")

    compiled = (
        compile_pattern(pattern, flags)
        if isinstance(pattern, str)
        else pattern
    )

    return compiled.split(text, maxsplit=max_splits)


def remove_matches(
    pattern: str | Pattern[str],
    text: str,
    flags: int = 0,
) -> str:
    """Remove all regex matches from text."""
    return replace_pattern(
        pattern,
        "",
        text,
        flags=flags,
    )


def _validate_text(text: Any) -> None:
    """Validate text input."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
