"""
Serialization utilities for Context-Aware Suggestion RAG.

Provides safe conversion of Python data structures into
JSON-compatible objects and serialized JSON strings.
"""

import json
from datetime import date, datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import UUID

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.exceptions import (
    ContextAwareSuggestionError,
)


# ---------------------------------------------------------
# Custom serialization error
# ---------------------------------------------------------

class SerializationError(ContextAwareSuggestionError):
    """Raised when serialization or deserialization fails."""


# ---------------------------------------------------------
# JSON default serializer
# ---------------------------------------------------------

def _json_default(value: Any) -> Any:
    """Convert supported Python objects into JSON-compatible values."""

    if isinstance(value, (datetime, date)):
        if isinstance(value, datetime) and value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)

        return value.isoformat()

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, UUID):
        return str(value)

    if isinstance(value, Path):
        return str(value)

    if isinstance(value, set):
        return list(value)

    if hasattr(value, "model_dump") and callable(value.model_dump):
        return value.model_dump(mode="json")

    raise TypeError(
        f"Object of type {type(value).__name__} is not JSON serializable."
    )


# ---------------------------------------------------------
# Dictionary serialization
# ---------------------------------------------------------

def to_json_compatible(data: Any) -> Any:
    """
    Convert supported Python objects into JSON-compatible data.

    The conversion passes through JSON encoding and decoding,
    ensuring that the returned value contains JSON-compatible types.
    """

    try:
        serialized = json.dumps(
            data,
            default=_json_default,
            ensure_ascii=False,
            allow_nan=False,
        )

        return json.loads(serialized)

    except (TypeError, ValueError, OverflowError) as exc:
        raise SerializationError(
            f"Failed to convert data into JSON-compatible format: {exc}"
        ) from exc


# ---------------------------------------------------------
# JSON string serialization
# ---------------------------------------------------------

def serialize_json(
    data: Any,
    indent: int | None = None,
) -> str:
    """Serialize Python data into a JSON string."""

    try:
        return json.dumps(
            data,
            default=_json_default,
            ensure_ascii=False,
            indent=indent,
            allow_nan=False,
        )

    except (TypeError, ValueError, OverflowError) as exc:
        raise SerializationError(
            f"JSON serialization failed: {exc}"
        ) from exc


# ---------------------------------------------------------
# JSON string deserialization
# ---------------------------------------------------------

def deserialize_json(
    json_string: str,
) -> Any:
    """Deserialize a JSON string into Python objects."""

    if not isinstance(json_string, str):
        raise SerializationError("JSON input must be a string.")

    try:
        return json.loads(json_string)

    except json.JSONDecodeError as exc:
        raise SerializationError(
            f"Invalid JSON input: {exc}"
        ) from exc


# ---------------------------------------------------------
# JSON file operations
# ---------------------------------------------------------

def save_json_file(
    data: Any,
    file_path: str | Path,
    indent: int = 4,
) -> None:
    """Save Python data as a JSON file."""

    path = Path(file_path)

    try:
        path.parent.mkdir(parents=True, exist_ok=True)

        serialized = serialize_json(data, indent=indent)
        path.write_text(serialized, encoding="utf-8")

    except (OSError, SerializationError) as exc:
        raise SerializationError(
            f"Failed to save JSON file '{path}': {exc}"
        ) from exc


def load_json_file(
    file_path: str | Path,
) -> Any:
    """Load and deserialize a JSON file."""

    path = Path(file_path)

    try:
        content = path.read_text(encoding="utf-8")

        return deserialize_json(content)

    except (OSError, SerializationError) as exc:
        raise SerializationError(
            f"Failed to load JSON file '{path}': {exc}"
        ) from exc


__all__ = [
    "SerializationError",
    "to_json_compatible",
    "serialize_json",
    "deserialize_json",
    "save_json_file",
    "load_json_file",
]
