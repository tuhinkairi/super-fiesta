
from datetime import date, datetime
from enum import Enum
from pathlib import Path

from context_aware_suggestion_rag.utils.converters import (
    to_boolean,
    to_datetime,
    to_dict,
    to_enum,
    to_float,
    to_integer,
    to_iso_string,
    to_json_string,
    to_list,
    to_path,
    to_string,
)


class Status(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


def test_to_string():
    assert to_string(123) == "123"
    assert to_string(None, "fallback") == "fallback"
    assert to_string({"a": 1}) == '{"a": 1}'


def test_to_integer():
    assert to_integer("42") == 42
    assert to_integer(10.0) == 10
    assert to_integer("invalid", 5) == 5
    assert to_integer(True, 7) == 7
    assert to_integer("12.5", 0) == 0


def test_to_float():
    assert to_float("3.14") == 3.14
    assert to_float("invalid", 2.5) == 2.5
    assert to_float(True, 1.0) == 1.0
    assert to_float(float("inf"), 0.0) == 0.0


def test_to_boolean():
    assert to_boolean("true") is True
    assert to_boolean("YES") is True
    assert to_boolean("off") is False
    assert to_boolean(1) is True
    assert to_boolean(0) is False
    assert to_boolean("unknown", False) is False


def test_to_enum():
    assert to_enum(Status, "active") is Status.ACTIVE
    assert to_enum(Status, "INACTIVE") is Status.INACTIVE
    assert to_enum(Status, "unknown", Status.ACTIVE) is Status.ACTIVE
    assert to_enum(Status, Status.ACTIVE) is Status.ACTIVE


def test_to_list():
    assert to_list(None) == []
    assert to_list("hello") == ["hello"]
    assert to_list("a,b,c", split_string=True) == ["a", "b", "c"]
    assert to_list((1, 2)) == [1, 2]


def test_to_dict():
    assert to_dict({"a": 1}) == {"a": 1}
    assert to_dict('{"a": 1}', parse_json=True) == {"a": 1}
    assert to_dict("invalid", parse_json=True) == {}
    assert to_dict(None, default={"fallback": True}) == {
        "fallback": True
    }


def test_to_path():
    assert to_path("documents/test.pdf") == Path("documents/test.pdf")
    assert to_path(None, Path("fallback")) == Path("fallback")


def test_to_datetime():
    value = datetime(2026, 1, 1)
    assert to_datetime(value) is value
    assert to_datetime(date(2026, 1, 1)) == datetime(2026, 1, 1)
    assert to_datetime("invalid") is None
    assert to_datetime("2026-01-01T10:30:00") == datetime(
        2026, 1, 1, 10, 30
    )


def test_to_iso_string():
    value = datetime(2026, 1, 1)
    assert to_iso_string(value) == "2026-01-01T00:00:00"
    assert to_iso_string(date(2026, 1, 1)) == "2026-01-01"


def test_to_json_string():
    result = to_json_string({"name": "RAG"}, indent=2)
    assert '"name": "RAG"' in result


if __name__ == "__main__":
    tests = [
        test_to_string,
        test_to_integer,
        test_to_float,
        test_to_boolean,
        test_to_enum,
        test_to_list,
        test_to_dict,
        test_to_path,
        test_to_datetime,
        test_to_iso_string,
        test_to_json_string,
    ]

    for test in tests:
        test()
        print(f"{test.__name__}: PASS")

    print("All converter utility tests passed.")
