
from datetime import datetime, timezone

from context_aware_suggestion_rag.utils.formatters import (
    format_bytes,
    format_number,
    format_percentage,
    normalize_whitespace,
    format_title,
    format_snake_case,
    format_camel_case,
    format_pascal_case,
    format_list,
    format_datetime_value,
    format_mapping,
    pretty_json,
    format_metadata,
    truncate_with_ellipsis,
)


def test_format_bytes():
    assert format_bytes(1024) == "1.00 KB"
    assert format_bytes(0) == "0.00 B"
    print("Byte formatting: PASS")


def test_format_number():
    assert format_number(1234567.891) == "1,234,567.89"
    assert format_number(1234.5, precision=1) == "1,234.5"
    print("Number formatting: PASS")


def test_format_percentage():
    assert format_percentage(0.75) == "75.00%"
    assert format_percentage(75, multiply_by_100=False) == "75.00%"
    print("Percentage formatting: PASS")


def test_whitespace_and_title():
    assert normalize_whitespace("  Hello   World  ") == "Hello World"
    assert format_title("  hello world  ") == "Hello world"
    print("Text normalization: PASS")


def test_case_formatting():
    assert format_snake_case("ContextAwareRAG") == "context_aware_rag"
    assert format_camel_case("context aware rag") == "contextAwareRag"
    assert format_pascal_case("context aware rag") == "ContextAwareRag"
    print("Case formatting: PASS")


def test_format_list():
    assert format_list(["AI", "ML", "RAG"]) == "AI, ML, RAG"
    assert format_list(
        ["AI", "ML", "RAG"],
        final_separator=" and ",
    ) == "AI, ML and RAG"
    print("List formatting: PASS")


def test_datetime_formatting():
    value = datetime(
        2026, 1, 1, 12, 30,
        tzinfo=timezone.utc,
    )

    assert format_datetime_value(value, format_string="%Y-%m-%d") == (
        "2026-01-01"
    )
    print("Date formatting: PASS")


def test_mapping_formatting():
    result = format_mapping(
        {"name": "RAG", "version": "1.0"},
        indent=2,
        sort_keys=True,
    )

    assert result == "  name: RAG\n  version: 1.0"
    print("Mapping formatting: PASS")


def test_pretty_json():
    result = pretty_json({"name": "RAG", "version": 1})

    assert '"name": "RAG"' in result
    assert '"version": 1' in result
    print("Pretty JSON formatting: PASS")


def test_metadata_formatting():
    result = format_metadata({
        "name": "RAG",
        "description": None,
    })

    assert result == {"name": "RAG"}
    print("Metadata formatting: PASS")


def test_truncation():
    assert truncate_with_ellipsis("Hello World", 8) == "Hello..."
    assert truncate_with_ellipsis("Hello", 10) == "Hello"
    print("Text truncation: PASS")


if __name__ == "__main__":
    test_format_bytes()
    test_format_number()
    test_format_percentage()
    test_whitespace_and_title()
    test_case_formatting()
    test_format_list()
    test_datetime_formatting()
    test_mapping_formatting()
    test_pretty_json()
    test_metadata_formatting()
    test_truncation()

    print("All utility formatter tests passed.")
