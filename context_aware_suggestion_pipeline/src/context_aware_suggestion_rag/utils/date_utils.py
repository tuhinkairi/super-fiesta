
"""Date and time utility functions."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from typing import Any


UTC = timezone.utc


def utc_now() -> datetime:
    """Return the current timezone-aware UTC datetime."""
    return datetime.now(UTC)


def utc_timestamp() -> float:
    """Return the current UTC Unix timestamp."""
    return utc_now().timestamp()


def ensure_aware(
    value: datetime,
    *,
    assume_timezone: timezone | ZoneInfo = UTC,
) -> datetime:
    """Ensure that a datetime has timezone information."""
    if not isinstance(value, datetime):
        raise TypeError("value must be a datetime.")

    if value.tzinfo is None or value.utcoffset() is None:
        return value.replace(tzinfo=assume_timezone)

    return value


def to_utc(value: datetime) -> datetime:
    """Convert a datetime to UTC."""
    return ensure_aware(value).astimezone(UTC)


def to_timezone(
    value: datetime,
    timezone_name: str,
) -> datetime:
    """Convert a datetime to a named timezone."""
    if not isinstance(timezone_name, str) or not timezone_name.strip():
        raise ValueError("timezone_name must be a non-empty string.")

    try:
        target_timezone = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError as exc:
        raise ValueError(
            f"Unknown timezone: {timezone_name}"
        ) from exc

    return ensure_aware(value).astimezone(target_timezone)


def parse_datetime(
    value: str | datetime,
    *,
    default_timezone: timezone | ZoneInfo = UTC,
) -> datetime:
    """Parse an ISO 8601 datetime and return an aware datetime."""
    if isinstance(value, datetime):
        return ensure_aware(value, assume_timezone=default_timezone)

    if not isinstance(value, str):
        raise TypeError("value must be a string or datetime.")

    normalized = value.strip()

    if not normalized:
        raise ValueError("Datetime string must not be empty.")

    if normalized.endswith(("Z", "z")):
        normalized = normalized[:-1] + "+00:00"

    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"Invalid ISO 8601 datetime: {value}") from exc

    return ensure_aware(parsed, assume_timezone=default_timezone)


def parse_date(value: str | date) -> date:
    """Parse an ISO 8601 date."""
    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    if not isinstance(value, str):
        raise TypeError("value must be a string or date.")

    try:
        return date.fromisoformat(value.strip())
    except ValueError as exc:
        raise ValueError(f"Invalid ISO 8601 date: {value}") from exc


def datetime_to_iso(value: datetime) -> str:
    """Convert a datetime to an ISO 8601 string."""
    if not isinstance(value, datetime):
        raise TypeError("value must be a datetime.")

    return value.isoformat()


def timestamp_to_datetime(
    timestamp: int | float,
    *,
    target_timezone: timezone | ZoneInfo = UTC,
) -> datetime:
    """Convert a Unix timestamp into an aware datetime."""
    if isinstance(timestamp, bool) or not isinstance(timestamp, (int, float)):
        raise TypeError("timestamp must be numeric.")

    try:
        result = datetime.fromtimestamp(timestamp, tz=UTC)
    except (OverflowError, OSError, ValueError) as exc:
        raise ValueError("Invalid Unix timestamp.") from exc

    return result.astimezone(target_timezone)


def datetime_to_timestamp(value: datetime) -> float:
    """Convert a datetime into a Unix timestamp."""
    return to_utc(value).timestamp()


def add_time(
    value: datetime,
    *,
    days: float = 0,
    hours: float = 0,
    minutes: float = 0,
    seconds: float = 0,
) -> datetime:
    """Add a duration to a datetime."""
    for name, amount in {
        "days": days,
        "hours": hours,
        "minutes": minutes,
        "seconds": seconds,
    }.items():
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            raise TypeError(f"{name} must be numeric.")

    return ensure_aware(value) + timedelta(
        days=days,
        hours=hours,
        minutes=minutes,
        seconds=seconds,
    )


def time_difference_seconds(
    start: datetime,
    end: datetime,
) -> float:
    """Return the difference between two datetimes in seconds."""
    return (to_utc(end) - to_utc(start)).total_seconds()


def is_expired(
    expires_at: datetime,
    *,
    reference_time: datetime | None = None,
) -> bool:
    """Check whether an expiration datetime has passed."""
    reference = to_utc(reference_time or utc_now())
    expiration = to_utc(expires_at)

    return expiration <= reference


def start_of_day(
    value: datetime,
    *,
    target_timezone: timezone | ZoneInfo | None = None,
) -> datetime:
    """Return midnight at the beginning of the datetime's local day."""
    current = ensure_aware(value)

    if target_timezone is not None:
        current = current.astimezone(target_timezone)

    return current.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )


def end_of_day(
    value: datetime,
    *,
    target_timezone: timezone | ZoneInfo | None = None,
) -> datetime:
    """Return the final microsecond of the datetime's local day."""
    return start_of_day(
        value,
        target_timezone=target_timezone,
    ) + timedelta(days=1) - timedelta(microseconds=1)


def is_same_day(
    first: datetime,
    second: datetime,
    *,
    target_timezone: timezone | ZoneInfo = UTC,
) -> bool:
    """Check whether two datetimes fall on the same local calendar day."""
    return (
        first.astimezone(target_timezone).date()
        == second.astimezone(target_timezone).date()
    )


def format_datetime(
    value: datetime,
    format_string: str = "%Y-%m-%d %H:%M:%S",
    *,
    target_timezone: timezone | ZoneInfo | None = None,
) -> str:
    """Format a datetime using a configurable format string."""
    if not isinstance(format_string, str):
        raise TypeError("format_string must be a string.")

    current = ensure_aware(value)

    if target_timezone is not None:
        current = current.astimezone(target_timezone)

    return current.strftime(format_string)
