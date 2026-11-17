"""
Centralized metadata utilities.

Provides metadata creation, merging, filtering, and validation
for document, trend, news, and recommendation records.
"""

from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Any

from context_aware_suggestion_rag.constants import (
    METADATA_CONTENT,
    METADATA_CREATED_AT,
    METADATA_DOCUMENT_ID,
    METADATA_SOURCE,
    METADATA_SOURCE_TYPE,
    METADATA_TITLE,
    SOURCE_DOCUMENT,
    SOURCE_NEWS,
    SOURCE_TREND,
)
from context_aware_suggestion_rag.core.time import utc_now
from context_aware_suggestion_rag.core.validators import validate_metadata


VALID_SOURCE_TYPES = frozenset({
    SOURCE_DOCUMENT,
    SOURCE_TREND,
    SOURCE_NEWS,
})


def create_metadata(
    source_type: str,
    *,
    source_id: str,
    title: str | None = None,
    content: str | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Create standardized metadata for a pipeline record.

    User-provided metadata cannot override reserved fields.
    """

    if source_type not in VALID_SOURCE_TYPES:
        raise ValueError(f"Unsupported source type: {source_type!r}")

    if not isinstance(source_id, str) or not source_id.strip():
        raise ValueError("source_id must be a non-empty string")

    reserved = {
        METADATA_SOURCE,
        METADATA_SOURCE_TYPE,
        METADATA_CREATED_AT,
        METADATA_TITLE,
        METADATA_CONTENT,
        METADATA_DOCUMENT_ID,
    }

    custom_metadata = dict(metadata or {})

    conflicting_keys = reserved.intersection(custom_metadata)

    if conflicting_keys:
        raise ValueError(
            "Custom metadata cannot override reserved keys: "
            + ", ".join(sorted(conflicting_keys))
        )

    result: dict[str, Any] = {
        METADATA_SOURCE: source_id,
        METADATA_SOURCE_TYPE: source_type,
        METADATA_CREATED_AT: utc_now().isoformat(),
    }

    if title is not None:
        result[METADATA_TITLE] = title

    if content is not None:
        result[METADATA_CONTENT] = content

    result.update(custom_metadata)

    return validate_metadata(result)


def merge_metadata(
    base_metadata: Mapping[str, Any],
    additional_metadata: Mapping[str, Any],
    *,
    overwrite: bool = False,
) -> dict[str, Any]:
    """
    Merge two metadata dictionaries.

    By default, existing values in base_metadata are preserved.
    """

    if not isinstance(base_metadata, Mapping):
        raise TypeError("base_metadata must be a mapping")

    if not isinstance(additional_metadata, Mapping):
        raise TypeError("additional_metadata must be a mapping")

    merged = dict(base_metadata)

    for key, value in additional_metadata.items():
        if overwrite or key not in merged:
            merged[key] = value

    return validate_metadata(merged)


def filter_metadata(
    metadata: Mapping[str, Any],
    allowed_keys: Sequence[str],
) -> dict[str, Any]:
    """Return metadata containing only explicitly allowed keys."""

    if not isinstance(metadata, Mapping):
        raise TypeError("metadata must be a mapping")

    if isinstance(allowed_keys, (str, bytes)):
        raise TypeError("allowed_keys must be a sequence of key names")

    allowed = set(allowed_keys)

    if not all(isinstance(key, str) for key in allowed):
        raise TypeError("All allowed metadata keys must be strings")

    return {
        key: value
        for key, value in metadata.items()
        if key in allowed
    }


def update_metadata_timestamp(
    metadata: Mapping[str, Any],
) -> dict[str, Any]:
    """Update the metadata updated_at timestamp."""

    if not isinstance(metadata, Mapping):
        raise TypeError("metadata must be a mapping")

    updated = dict(metadata)
    updated["updated_at"] = utc_now().isoformat()

    return validate_metadata(updated)


__all__ = [
    "VALID_SOURCE_TYPES",
    "create_metadata",
    "merge_metadata",
    "filter_metadata",
    "update_metadata_timestamp",
]
