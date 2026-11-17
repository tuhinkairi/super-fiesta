"""Formatting utilities for text and structured data."""

from __future__ import annotations

import json
import math
import re
from collections.abc import Mapping, Sequence
from datetime import date, datetime
from pathlib import Path
from typing import Any


def format_bytes(size: int, *, precision: int = 2) -> str:
    """Format a byte count using human-readable units."""
    if isinstance(size, bool) or not isinstance(size, int):
        raise TypeError("size must be an integer.")

    if size < 0:
        raise ValueError("size must not be negative.")

    if isinstance(precision, bool) or not isinstance(precision, int):
        raise TypeError("precision must be an integer.")

    if precision < 0:
        raise ValueError("precision must not be negative.")

    units = ("B", "KB", "MB", "GB", "TB", "PB")
    value = float(size)

    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.{precision}f} {unit}"
        value /= 1024

    return f"{value:.{precision}f} PB"


def format_number(
    value: int | float,
    *,
    precision: int = 2,
    thousands_separator: str = ",",
) -> str:
    """Format a finite number with configurable precision."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError("value must be numeric.")

    if not math.isfinite(value):
        raise ValueError("value must be finite.")

    if isinstance(precision, bool) or not isinstance(precision, int):
        raise TypeError("precision must be an integer.")

    if precision < 0:
        raise ValueError("precision must not be negative.")

    if not isinstance(thousands_separator, str):
        raise TypeError("thousands_separator must be a string.")

    formatted = f"{value:,.{precision}f}"

    if thousands_separator != ",":
        formatted = formatted.replace(",", thousands_separator)

    return formatted


def format_percentage(
    value: int | float,
    *,
    precision: int = 2,
    multiply_by_100: bool = True,
) -> str:
    """Format a proportion or percentage."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError("value must be numeric.")

    if not math.isfinite(value):
        raise ValueError("value must be finite.")

    percentage = value * 100 if multiply_by_100 else value

    return f"{percentage:.{precision}f}%"


def normalize_whitespace(text: str) -> str:
    """Collapse repeated whitespace into single spaces."""
    if not isinstance(text, str):
        raise TypeError("text must be a string.")

    return " ".join(text.split())


def format_title(text: str) -> str:
    """Normalize text and capitalize its first character."""
    normalized = normalize_whitespace(text)

    if not normalized:
        return ""

    return normalized[0].upper() + normalized[1:]


def format_snake_case(text: str) -> str:
    """Convert text into snake_case."""
    if not isinstance(text, str):
        raise TypeError("text must be a string.")

    text = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", text)
    text = re.sub(r"([A-Z])([A-Z][a-z])", r"\1_\2", text)

    return re.sub(r"[\W]+", "_", text).strip("_").lower()


def format_camel_case(text: str) -> str:
    """Convert text into camelCase."""
    if not isinstance(text, str):
        raise TypeError("text must be a string.")

    words = re.findall(r"[A-Za-z0-9]+", text)

    if not words:
        return ""

    first = words[0].lower()
    remaining = [word.capitalize() for word in words[1:]]

    return first + "".join(remaining)


def format_pascal_case(text: str) -> str:
    """Convert text into PascalCase."""
    if not isinstance(text, str):
        raise TypeError("text must be a string.")

    words = re.findall(r"[A-Za-z0-9]+", text)

    return "".join(word.capitalize() for word in words)


def format_list(
    items: Sequence[Any],
    *,
    separator: str = ", ",
    final_separator: str | None = None,
) -> str:
    """Format a sequence as readable text."""
    if isinstance(items, (str, bytes, bytearray)) or not isinstance(
        items,
        Sequence,
    ):
        raise TypeError("items must be a non-string sequence.")

    if not isinstance(separator, str):
        raise TypeError("separator must be a string.")

    if final_separator is not None and not isinstance(final_separator, str):
        raise TypeError("final_separator must be a string or None.")

    values = [str(item) for item in items]

    if len(values) <= 1:
        return "".join(values)

    if final_separator is None:
        return separator.join(values)

    return separator.join(values[:-1]) + final_separator + values[-1]


def format_datetime_value(
    value: datetime | date,
    *,
    format_string: str = "%Y-%m-%d %H:%M:%S",
) -> str:
    """Format a date or datetime."""
    if not isinstance(value, (datetime, date)):
        raise TypeError("value must be a date or datetime.")

    if not isinstance(format_string, str):
        raise TypeError("format_string must be a string.")

    return value.strftime(format_string)


def format_mapping(
    data: Mapping[str, Any],
    *,
    indent: int = 0,
    sort_keys: bool = False,
) -> str:
    """Format a mapping as readable key-value lines."""
    if not isinstance(data, Mapping):
        raise TypeError("data must be a mapping.")

    if isinstance(indent, bool) or not isinstance(indent, int) or indent < 0:
        raise ValueError("indent must be a non-negative integer.")

    items = list(data.items())

    if sort_keys:
        items.sort(key=lambda item: str(item[0]))

    prefix = " " * indent

    return "\n".join(
        f"{prefix}{key}: {value}"
        for key, value in items
    )


def pretty_json(
    value: Any,
    *,
    indent: int = 2,
    ensure_ascii: bool = False,
) -> str:
    """Return indented JSON."""
    if isinstance(indent, bool) or not isinstance(indent, int) or indent < 0:
        raise ValueError("indent must be a non-negative integer.")

    def _default(obj: Any) -> Any:
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()

        if isinstance(obj, Path):
            return str(obj)

        if hasattr(obj, "model_dump") and callable(obj.model_dump):
            return obj.model_dump(mode="json")

        if hasattr(obj, "value"):
            return obj.value

        raise TypeError(
            f"Object of type {type(obj).__name__} is not JSON serializable."
        )

    return json.dumps(
        value,
        indent=indent,
        ensure_ascii=ensure_ascii,
        default=_default,
        allow_nan=False,
    )


def format_metadata(
    metadata: Mapping[str, Any],
    *,
    exclude_none: bool = True,
) -> dict[str, Any]:
    """Return normalized metadata suitable for display or serialization."""
    if not isinstance(metadata, Mapping):
        raise TypeError("metadata must be a mapping.")

    result: dict[str, Any] = {}

    for key, value in metadata.items():
        if not isinstance(key, str):
            raise TypeError("Metadata keys must be strings.")

        if exclude_none and value is None:
            continue

        result[key.strip()] = value

    return result


def truncate_with_ellipsis(
    text: str,
    max_length: int,
    *,
    suffix: str = "...",
) -> str:
    """Truncate text without exceeding the specified length."""
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
