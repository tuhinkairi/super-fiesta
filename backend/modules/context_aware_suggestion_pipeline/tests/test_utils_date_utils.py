
from datetime import date, datetime, timedelta, timezone

from context_aware_suggestion_rag.utils.date_utils import (
    utc_now,
    utc_timestamp,
    ensure_aware,
    to_utc,
    to_timezone,
    parse_datetime,
    parse_date,
    datetime_to_iso,
    timestamp_to_datetime,
    datetime_to_timestamp,
    add_time,
    time_difference_seconds,
    is_expired,
    start_of_day,
    end_of_day,
    is_same_day,
    format_datetime,
)


def test_utc_helpers():
    now = utc_now()

    assert now.tzinfo is not None
    assert now.utcoffset() == timedelta(0)
    assert isinstance(utc_timestamp(), float)

    print("UTC helpers: PASS")


def test_timezone_conversion():
    naive = datetime(2026, 1, 1, 12, 0, 0)

    aware = ensure_aware(naive)
    assert aware.utcoffset() == timedelta(0)

    utc_value = to_utc(aware)
    kolkata_value = to_timezone(utc_value, "Asia/Kolkata")

    assert kolkata_value.hour == 17
    assert kolkata_value.minute == 30

    print("Timezone conversion: PASS")


def test_datetime_parsing():
    parsed = parse_datetime("2026-01-01T12:00:00Z")

    assert parsed.tzinfo is not None
    assert parsed.hour == 12

    print("Datetime parsing: PASS")


def test_date_parsing():
    parsed = parse_date("2026-01-01")

    assert parsed == date(2026, 1, 1)

    print("Date parsing: PASS")


def test_iso_and_timestamp_conversion():
    original = datetime(
        2026, 1, 1, 12, 0, 0,
        tzinfo=timezone.utc,
    )

    iso_value = datetime_to_iso(original)
    restored = parse_datetime(iso_value)

    assert restored == original

    timestamp = datetime_to_timestamp(original)
    restored_timestamp = timestamp_to_datetime(timestamp)

    assert restored_timestamp == original

    print("ISO and timestamp conversion: PASS")


def test_add_time():
    original = datetime(
        2026, 1, 1, 12, 0,
        tzinfo=timezone.utc,
    )

    result = add_time(original, days=1, hours=2)

    assert result == original + timedelta(days=1, hours=2)

    print("Time addition: PASS")


def test_time_difference():
    start = datetime(
        2026, 1, 1, 10,
        tzinfo=timezone.utc,
    )
    end = datetime(
        2026, 1, 1, 12,
        tzinfo=timezone.utc,
    )

    assert time_difference_seconds(start, end) == 7200

    print("Time difference: PASS")


def test_expiration():
    reference = datetime(
        2026, 1, 1, 12,
        tzinfo=timezone.utc,
    )

    expired = reference - timedelta(seconds=1)
    future = reference + timedelta(seconds=10)

    assert is_expired(expired, reference_time=reference)
    assert not is_expired(future, reference_time=reference)

    print("Expiration checking: PASS")


def test_day_boundaries():
    value = datetime(
        2026, 1, 1, 15, 30,
        tzinfo=timezone.utc,
    )

    beginning = start_of_day(value)
    ending = end_of_day(value)

    assert beginning.hour == 0
    assert beginning.minute == 0
    assert ending.hour == 23
    assert ending.minute == 59
    assert ending.microsecond == 999999

    print("Day boundary calculation: PASS")


def test_same_day():
    first = datetime(
        2026, 1, 1, 10,
        tzinfo=timezone.utc,
    )
    second = datetime(
        2026, 1, 1, 20,
        tzinfo=timezone.utc,
    )

    assert is_same_day(first, second)

    print("Same-day checking: PASS")


def test_datetime_formatting():
    value = datetime(
        2026, 1, 1, 12, 30,
        tzinfo=timezone.utc,
    )

    result = format_datetime(value, "%Y-%m-%d")

    assert result == "2026-01-01"

    print("Datetime formatting: PASS")


if __name__ == "__main__":
    test_utc_helpers()
    test_timezone_conversion()
    test_datetime_parsing()
    test_date_parsing()
    test_iso_and_timestamp_conversion()
    test_add_time()
    test_time_difference()
    test_expiration()
    test_day_boundaries()
    test_same_day()
    test_datetime_formatting()

    print("All date utility tests passed.")
