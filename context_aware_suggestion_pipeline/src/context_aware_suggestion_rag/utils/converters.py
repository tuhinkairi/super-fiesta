"""Reusable data conversion utilities."""

import json
import math
from collections.abc import Mapping
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Any, TypeVar

T = TypeVar("T")


def to_string(value: Any, default: str = "") -> str:
    """Convert a value to a string."""
    if value is None:
        return default

    if isinstance(value, str):
        return value

    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, ensure_ascii=False, default=str)

    return str(value)


def to_integer(
    value: Any,
    default: int | None = None,
) -> int | None:
    """Convert a value to an integer."""
    if value is None or isinstance(value, bool):
        return default

    try:
        if isinstance(value, float) and not math.isfinite(value):
            return default

        if isinstance(value, str):
            value = value.strip()
            if not value:
                return default

        return int(value)
    except (TypeError, ValueError, OverflowError):
        return default


def to_float(
    value: Any,
    default: float | None = None,
) -> float | None:
    """Convert a value to a finite float."""
    if value is None or isinstance(value, bool):
        return default

    try:
        converted = float(value)
        return converted if math.isfinite(converted) else default
    except (TypeError, ValueError, OverflowError):
        return default


def to_boolean(
    value: Any,
    default: bool | None = None,
) -> bool | None:
    """Convert common textual and numeric representations to bool."""
    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if value == 1:
            return True
        if value == 0:
            return False
        return default

    if isinstance(value, str):
        normalized = value.strip().lower()

        if normalized in {"true", "yes", "y", "1", "on"}:
            return True

        if normalized in {"false", "no", "n", "0", "off"}:
            return False

    return default


def to_enum(
    enum_class: type[T],
    value: Any,
    default: T | None = None,
) -> T | None:
    """Convert a value into an enum member."""
    if not isinstance(enum_class, type) or not issubclass(enum_class, Enum):
        raise TypeError("enum_class must be an Enum subclass")

    if isinstance(value, enum_class):
        return value

    if value is None:
        return default

    try:
        return enum_class(value)
    except (ValueError, TypeError):
        if isinstance(value, str):
            try:
                return enum_class[value.strip().upper()]
            except KeyError:
                pass

    return default


def to_list(
    value: Any,
    *,
    split_string: bool = False,
    separator: str = ",",
) -> list[Any]:
    """Convert a value into a list."""
    if value is None:
        return []

    if isinstance(value, list):
        return value.copy()

    if isinstance(value, (tuple, set, frozenset)):
        return list(value)

    if isinstance(value, str) and split_string:
        return [
            item.strip()
            for item in value.split(separator)
            if item.strip()
        ]

    return [value]


def to_dict(
    value: Any,
    *,
    parse_json: bool = False,
    default: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Convert a mapping or JSON object string into a dictionary."""
    if isinstance(value, Mapping):
        return dict(value)

    if isinstance(value, str) and parse_json:
        try:
            parsed = json.loads(value)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass

    return dict(default) if default is not None else {}


def to_path(
    value: Any,
    default: Path | None = None,
) -> Path | None:
    """Convert a value to pathlib.Path."""
    if value is None:
        return default

    try:
        return Path(value)
    except (TypeError, ValueError, OSError):
        return default


def to_datetime(
    value: Any,
    default: datetime | None = None,
) -> datetime | None:
    """Convert supported values into a datetime."""
    if isinstance(value, datetime):
        return value

    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        try:
            if not math.isfinite(value):
                return default
            return datetime.fromtimestamp(value).astimezone()
        except (ValueError, OverflowError, OSError):
            return default

    if isinstance(value, str):
        normalized = value.strip()

        if not normalized:
            return default

        try:
            return datetime.fromisoformat(
                normalized.replace("Z", "+00:00")
            )
        except ValueError:
            return default

    return default


def to_iso_string(value: Any, default: str | None = None) -> str | None:
    """Convert a date or datetime to ISO 8601 text."""
    if isinstance(value, (datetime, date)):
        return value.isoformat()

    return default


def to_json_string(
    value: Any,
    *,
    indent: int | None = None,
    ensure_ascii: bool = False,
) -> str:
    """Serialize a value to JSON."""
    return json.dumps(
        value,
        indent=indent,
        ensure_ascii=ensure_ascii,
        default=str,
    )
