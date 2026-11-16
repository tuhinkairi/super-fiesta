"""
Centralized identifier generation utilities.

Provides UUID-based identifiers for documents, chunks,
recommendations, requests, and other pipeline entities.
"""

import re
import uuid
from typing import Final


DEFAULT_PREFIX: Final[str] = "casr"

PREFIX_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"^[a-zA-Z][a-zA-Z0-9_-]{0,31}$"
)


def generate_id(prefix: str = DEFAULT_PREFIX) -> str:
    """
    Generate a unique identifier with a readable prefix.

    Example:
        casr_550e8400-e29b-41d4-a716-446655440000
    """

    validate_prefix(prefix)

    return f"{prefix}_{uuid.uuid4()}"


def generate_document_id() -> str:
    """Generate a document identifier."""
    return generate_id("doc")


def generate_chunk_id() -> str:
    """Generate a document chunk identifier."""
    return generate_id("chunk")


def generate_trend_id() -> str:
    """Generate a trend record identifier."""
    return generate_id("trend")


def generate_news_id() -> str:
    """Generate a news record identifier."""
    return generate_id("news")


def generate_recommendation_id() -> str:
    """Generate a recommendation identifier."""
    return generate_id("rec")


def generate_request_id() -> str:
    """Generate a pipeline request identifier."""
    return generate_id("req")


def generate_content_id() -> str:
    """Generate a generated-content identifier."""
    return generate_id("content")


def validate_prefix(prefix: str) -> None:
    """Validate an identifier prefix."""

    if not isinstance(prefix, str):
        raise TypeError("Identifier prefix must be a string")

    if not PREFIX_PATTERN.fullmatch(prefix):
        raise ValueError(
            "Prefix must start with a letter and contain only "
            "letters, numbers, underscores, or hyphens "
            "(maximum 32 characters)"
        )


__all__ = [
    "DEFAULT_PREFIX",
    "generate_id",
    "generate_document_id",
    "generate_chunk_id",
    "generate_trend_id",
    "generate_news_id",
    "generate_recommendation_id",
    "generate_request_id",
    "generate_content_id",
    "validate_prefix",
]
