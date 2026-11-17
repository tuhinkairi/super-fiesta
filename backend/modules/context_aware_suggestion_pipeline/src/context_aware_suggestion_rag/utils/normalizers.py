"""Normalization utilities for text and structured data."""

import re
import unicodedata
from collections.abc import Mapping
from typing import Any
from urllib.parse import urlsplit, urlunsplit


def normalize_unicode(text: str, form: str = "NFKC") -> str:
    """Normalize Unicode characters."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    if form not in {"NFC", "NFD", "NFKC", "NFKD"}:
        raise ValueError("Unsupported Unicode normalization form")

    return unicodedata.normalize(form, text)


def normalize_whitespace(text: str) -> str:
    """Replace consecutive whitespace with a single space."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    return re.sub(r"\s+", " ", text).strip()


def normalize_keyword(keyword: str) -> str:
    """Normalize a keyword for matching and deduplication."""
    if not isinstance(keyword, str):
        raise TypeError("keyword must be a string")

    normalized = normalize_unicode(keyword)
    normalized = normalize_whitespace(normalized)

    return normalized.casefold()


def normalize_identifier(identifier: str) -> str:
    """Normalize an identifier into lowercase underscore-separated text."""
    if not isinstance(identifier, str):
        raise TypeError("identifier must be a string")

    normalized = normalize_unicode(identifier)
    normalized = normalized.strip().casefold()
    normalized = re.sub(r"[\s\-]+", "_", normalized)
    normalized = re.sub(r"[^\w.]", "", normalized)
    normalized = re.sub(r"_+", "_", normalized)

    return normalized.strip("_")


def normalize_metadata_keys(
    metadata: Mapping[str, Any],
    *,
    lowercase: bool = True,
) -> dict[str, Any]:
    """Normalize metadata keys while preserving their values."""
    if not isinstance(metadata, Mapping):
        raise TypeError("metadata must be a mapping")

    result: dict[str, Any] = {}

    for key, value in metadata.items():
        if not isinstance(key, str):
            raise TypeError("metadata keys must be strings")

        normalized_key = normalize_whitespace(key)

        if lowercase:
            normalized_key = normalized_key.casefold()

        if not normalized_key:
            raise ValueError("metadata keys cannot be empty")

        if normalized_key in result:
            raise ValueError(
                f"Duplicate metadata key after normalization: {normalized_key}"
            )

        result[normalized_key] = value

    return result


def normalize_url(url: str, *, remove_fragment: bool = True) -> str:
    """Normalize a URL without changing its destination host or path."""
    if not isinstance(url, str):
        raise TypeError("url must be a string")

    url = url.strip()

    if not url:
        raise ValueError("url cannot be empty")

    parsed = urlsplit(url)

    if parsed.scheme.lower() not in {"http", "https"}:
        raise ValueError("Only HTTP and HTTPS URLs are supported")

    if not parsed.hostname:
        raise ValueError("URL must contain a hostname")

    if parsed.username is not None or parsed.password is not None:
        raise ValueError("URLs containing credentials are not supported")

    scheme = parsed.scheme.lower()
    hostname = parsed.hostname.lower()

    if ":" in hostname and not hostname.startswith("["):
        hostname = f"[{hostname}]"

    try:
        port = parsed.port
    except ValueError as error:
        raise ValueError("URL contains an invalid port") from error

    if port is not None:
        default_port = (
            (scheme == "http" and port == 80)
            or (scheme == "https" and port == 443)
        )
        if not default_port:
            hostname = f"{hostname}:{port}"

    netloc = hostname

    fragment = "" if remove_fragment else parsed.fragment

    return urlunsplit(
        (
            scheme,
            netloc,
            parsed.path or "/",
            parsed.query,
            fragment,
        )
    )


def normalize_text_for_search(text: str) -> str:
    """Normalize text for case-insensitive search."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    normalized = normalize_unicode(text)
    normalized = normalized.casefold()
    normalized = normalize_whitespace(normalized)

    return normalized


def normalize_tags(tags: list[str]) -> list[str]:
    """Normalize and deduplicate tags while preserving their order."""
    if not isinstance(tags, list):
        raise TypeError("tags must be a list")

    result: list[str] = []
    seen: set[str] = set()

    for tag in tags:
        if not isinstance(tag, str):
            raise TypeError("each tag must be a string")

        normalized = normalize_keyword(tag)

        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(normalized)

    return result
