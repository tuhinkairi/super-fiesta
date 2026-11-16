"""
Centralized date and time utilities.

Uses timezone-aware datetime objects and UTC as the standard
internal timezone for consistent timestamp handling.
"""

from datetime import datetime, timezone
from typing import Final
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


UTC: Final = timezone.utc


def utc_now() -> datetime:
    """Return the current timezone-aware UTC datetime."""
    return datetime.now(UTC)


def to_utc(value: datetime) -> datetime:
    """
    Convert a datetime to UTC.

    Naive datetimes are rejected because their timezone is ambiguous.
    """
    if not isinstance(value, datetime):
        raise TypeError("value must be a datetime")

    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(
            "Naive datetime is not allowed; provide timezone information"
        )

    return value.astimezone(UTC)


def to_iso_string(value: datetime) -> str:
    """Convert a datetime to an ISO 8601 UTC string."""
    return to_utc(value).isoformat()


def from_iso_string(value: str) -> datetime:
    """Parse an ISO 8601 timestamp and normalize it to UTC."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Timestamp must be a non-empty string")

    try:
        parsed = datetime.fromisoformat(value.strip())
    except ValueError as exc:
        raise ValueError(
            f"Invalid ISO 8601 timestamp: {value!r}"
        ) from exc

    return to_utc(parsed)


def from_unix_timestamp(value: int | float) -> datetime:
    """Convert a Unix timestamp into a timezone-aware UTC datetime."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError("Unix timestamp must be an integer or float")

    try:
        return datetime.fromtimestamp(value, tz=UTC)
    except (OverflowError, OSError, ValueError) as exc:
        raise ValueError("Unix timestamp is outside the supported range") from exc


def to_unix_timestamp(value: datetime) -> float:
    """Convert a timezone-aware datetime to a Unix timestamp."""
    return to_utc(value).timestamp()


def to_timezone(value: datetime, timezone_name: str) -> datetime:
    """Convert a datetime into the requested IANA timezone."""
    if not isinstance(timezone_name, str) or not timezone_name.strip():
        raise ValueError("Timezone name must be a non-empty string")

    try:
        target_timezone = ZoneInfo(timezone_name)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise ValueError(
            f"Unknown or invalid timezone: {timezone_name!r}"
        ) from exc

    return to_utc(value).astimezone(target_timezone)


def seconds_between(
    start: datetime,
    end: datetime,
) -> float:
    """Return the elapsed time in seconds between two datetimes."""
    return (to_utc(end) - to_utc(start)).total_seconds()


def is_expired(
    expires_at: datetime,
    reference_time: datetime | None = None,
) -> bool:
    """Check whether a timestamp has expired."""
    expiry = to_utc(expires_at)
    reference = to_utc(reference_time) if reference_time else utc_now()

    return expiry <= reference


__all__ = [
    "UTC",
    "utc_now",
    "to_utc",
    "to_iso_string",
    "from_iso_string",
    "from_unix_timestamp",
    "to_unix_timestamp",
    "to_timezone",
    "seconds_between",
    "is_expired",
]
