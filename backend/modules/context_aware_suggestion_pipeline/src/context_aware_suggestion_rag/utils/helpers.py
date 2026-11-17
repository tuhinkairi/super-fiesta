"""General-purpose helper functions."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from copy import deepcopy
from datetime import date, datetime
from pathlib import Path
from typing import Any, TypeVar


T = TypeVar("T")


def deep_copy(value: T) -> T:
    """Return an independent deep copy of a value."""
    return deepcopy(value)


def safe_get(
    data: Mapping[str, Any],
    key: str,
    default: T | None = None,
) -> Any | T | None:
    """Retrieve a mapping value without raising KeyError."""
    if not isinstance(data, Mapping):
        raise TypeError("data must be a mapping.")

    if not isinstance(key, str):
        raise TypeError("key must be a string.")

    return data.get(key, default)


def nested_get(
    data: Mapping[str, Any],
    path: str | Sequence[str],
    default: T | None = None,
) -> Any | T | None:
    """Retrieve a nested mapping value using a dotted path."""
    if not isinstance(data, Mapping):
        raise TypeError("data must be a mapping.")

    if isinstance(path, str):
        parts = path.split(".")
    elif isinstance(path, Sequence) and not isinstance(path, (bytes, bytearray)):
        parts = list(path)
    else:
        raise TypeError("path must be a string or sequence of strings.")

    if not parts or any(not isinstance(part, str) or not part for part in parts):
        raise ValueError("path must contain non-empty string components.")

    current: Any = data

    for part in parts:
        if not isinstance(current, Mapping) or part not in current:
            return default

        current = current[part]

    return current


def nested_set(
    data: dict[str, Any],
    path: str | Sequence[str],
    value: Any,
    *,
    overwrite: bool = True,
) -> dict[str, Any]:
    """Set a nested mapping value, creating intermediate dictionaries."""
    if not isinstance(data, dict):
        raise TypeError("data must be a dictionary.")

    if isinstance(path, str):
        parts = path.split(".")
    elif isinstance(path, Sequence) and not isinstance(path, (bytes, bytearray)):
        parts = list(path)
    else:
        raise TypeError("path must be a string or sequence of strings.")

    if not parts or any(not isinstance(part, str) or not part for part in parts):
        raise ValueError("path must contain non-empty string components.")

    current = data

    for part in parts[:-1]:
        existing = current.get(part)

        if existing is None:
            current[part] = {}
        elif not isinstance(existing, dict):
            raise ValueError(
                f"Cannot create nested value: '{part}' is not a dictionary."
            )

        current = current[part]

    final_key = parts[-1]

    if not overwrite and final_key in current:
        raise ValueError(f"Key '{final_key}' already exists.")

    current[final_key] = value
    return data


def flatten_dict(
    data: Mapping[str, Any],
    *,
    separator: str = ".",
) -> dict[str, Any]:
    """Flatten nested dictionaries into dotted-key dictionaries."""
    if not isinstance(data, Mapping):
        raise TypeError("data must be a mapping.")

    if not isinstance(separator, str) or not separator:
        raise ValueError("separator must be a non-empty string.")

    flattened: dict[str, Any] = {}

    def _flatten(current: Mapping[str, Any], prefix: str = "") -> None:
        for key, value in current.items():
            if not isinstance(key, str):
                raise TypeError("All dictionary keys must be strings.")

            full_key = f"{prefix}{separator}{key}" if prefix else key

            if isinstance(value, Mapping):
                _flatten(value, full_key)
            else:
                flattened[full_key] = value

    _flatten(data)
    return flattened


def chunk_sequence(
    items: Sequence[T],
    chunk_size: int,
) -> list[list[T]]:
    """Split a sequence into fixed-size lists."""
    if isinstance(items, (str, bytes, bytearray)) or not isinstance(items, Sequence):
        raise TypeError("items must be a non-string sequence.")

    if isinstance(chunk_size, bool) or not isinstance(chunk_size, int):
        raise TypeError("chunk_size must be an integer.")

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    return [
        list(items[index:index + chunk_size])
        for index in range(0, len(items), chunk_size)
    ]


def unique_preserve_order(items: Sequence[T]) -> list[T]:
    """Remove duplicate hashable items while preserving order."""
    if isinstance(items, (str, bytes, bytearray)) or not isinstance(items, Sequence):
        raise TypeError("items must be a non-string sequence.")

    result: list[T] = []
    seen: set[Any] = set()

    for item in items:
        try:
            if item not in seen:
                seen.add(item)
                result.append(item)
        except TypeError as exc:
            raise TypeError("All items must be hashable.") from exc

    return result


def merge_dicts(
    *mappings: Mapping[str, Any],
    deep: bool = False,
) -> dict[str, Any]:
    """Merge mappings from left to right; later values take precedence."""
    merged: dict[str, Any] = {}

    for mapping in mappings:
        if not isinstance(mapping, Mapping):
            raise TypeError("All arguments must be mappings.")

        for key, value in mapping.items():
            if not isinstance(key, str):
                raise TypeError("All mapping keys must be strings.")

            if (
                deep
                and isinstance(value, Mapping)
                and isinstance(merged.get(key), Mapping)
            ):
                merged[key] = merge_dicts(
                    merged[key],
                    value,
                    deep=True,
                )
            else:
                merged[key] = deepcopy(value) if deep else value

    return merged


def to_json(
    value: Any,
    *,
    indent: int | None = None,
    ensure_ascii: bool = False,
) -> str:
    """Serialize a value to JSON."""
    if indent is not None and (
        isinstance(indent, bool) or not isinstance(indent, int) or indent < 0
    ):
        raise ValueError("indent must be a non-negative integer or None.")

    def _default(obj: Any) -> Any:
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()

        if isinstance(obj, Path):
            return str(obj)

        if hasattr(obj, "model_dump") and callable(obj.model_dump):
            return obj.model_dump(mode="json")

        if hasattr(obj, "to_dict") and callable(obj.to_dict):
            return obj.to_dict()

        if hasattr(obj, "value"):
            return obj.value

        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable.")

    return json.dumps(
        value,
        default=_default,
        indent=indent,
        ensure_ascii=ensure_ascii,
        allow_nan=False,
    )


def from_json(value: str) -> Any:
    """Deserialize JSON text."""
    if not isinstance(value, str):
        raise TypeError("value must be a string.")

    return json.loads(value)


def slugify(
    value: str,
    *,
    separator: str = "-",
) -> str:
    """Convert text into a URL-friendly slug."""
    if not isinstance(value, str):
        raise TypeError("value must be a string.")

    if not isinstance(separator, str) or not separator:
        raise ValueError("separator must be a non-empty string.")

    normalized = value.strip().lower()
    normalized = re.sub(r"[^\w\s-]", "", normalized)
    normalized = re.sub(r"[\s_-]+", separator, normalized)

    return normalized.strip(separator)


def truncate_text(
    text: str,
    max_length: int,
    *,
    suffix: str = "...",
) -> str:
    """Truncate text to a maximum character count."""
    if not isinstance(text, str):
        raise TypeError("text must be a string.")

    if isinstance(max_length, bool) or not isinstance(max_length, int):
        raise TypeError("max_length must be an integer.")

    if max_length < 0:
        raise ValueError("max_length must not be negative.")

    if not isinstance(suffix, str):
        raise TypeError("suffix must be a string.")

    if len(text) <= max_length:
        return text

    if max_length == 0:
        return ""

    if len(suffix) >= max_length:
        return suffix[:max_length]

    return text[:max_length - len(suffix)].rstrip() + suffix


def get_type_name(value: Any) -> str:
    """Return the fully qualified type name of an object."""
    value_type = type(value)
    return f"{value_type.__module__}.{value_type.__qualname__}"


def is_iterable(value: Any, *, include_strings: bool = False) -> bool:
    """Check whether a value is iterable."""
    try:
        iter(value)
    except TypeError:
        return False

    if not include_strings and isinstance(value, (str, bytes, bytearray)):
        return False

    return True
