
from pathlib import Path

from context_aware_suggestion_rag.utils.validators import (
    validate_not_none,
    validate_non_empty_string,
    validate_identifier,
    validate_positive_integer,
    validate_non_negative_integer,
    validate_positive_number,
    validate_non_negative_number,
    validate_probability,
    validate_url,
    validate_path,
    validate_mapping,
    validate_sequence,
    validate_choice,
)


def test_string_validation():
    assert validate_non_empty_string(" hello ") == "hello"

    try:
        validate_non_empty_string(" ")
    except ValueError:
        pass
    else:
        raise AssertionError("Empty string should fail.")

    print("String validation: PASS")


def test_identifier_validation():
    assert validate_identifier("document_123") == "document_123"

    try:
        validate_identifier("../document")
    except ValueError:
        pass
    else:
        raise AssertionError("Unsafe identifier should fail.")

    print("Identifier validation: PASS")


def test_integer_validation():
    assert validate_positive_integer(10) == 10
    assert validate_non_negative_integer(0) == 0

    for invalid in (True, 0, -1):
        try:
            validate_positive_integer(invalid)
        except (TypeError, ValueError):
            pass
        else:
            raise AssertionError("Invalid positive integer accepted.")

    print("Integer validation: PASS")


def test_number_validation():
    assert validate_positive_number(2.5) == 2.5
    assert validate_non_negative_number(0) == 0.0
    assert validate_probability(0.75) == 0.75

    for invalid in (float("nan"), float("inf"), -1):
        try:
            validate_non_negative_number(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid number accepted.")

    print("Numeric validation: PASS")


def test_url_validation():
    assert validate_url("https://example.com") == "https://example.com"

    try:
        validate_url("ftp://example.com")
    except ValueError:
        pass
    else:
        raise AssertionError("Unsupported URL scheme accepted.")

    print("URL validation: PASS")


def test_path_validation():
    path = validate_path("some-folder")
    assert isinstance(path, Path)

    try:
        validate_path("missing-file.txt", must_exist=True)
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("Missing path should fail.")

    print("Path validation: PASS")


def test_mapping_validation():
    assert validate_mapping({"name": "test"})["name"] == "test"

    try:
        validate_mapping([])
    except TypeError:
        pass
    else:
        raise AssertionError("Invalid mapping accepted.")

    print("Mapping validation: PASS")


def test_sequence_validation():
    assert validate_sequence([1, 2, 3], item_type=int) == [1, 2, 3]

    try:
        validate_sequence("hello")
    except TypeError:
        pass
    else:
        raise AssertionError("String should not count as a sequence.")

    print("Sequence validation: PASS")


def test_choice_validation():
    assert validate_choice("pdf", ["pdf", "docx"]) == "pdf"

    try:
        validate_choice("exe", ["pdf", "docx"])
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid choice accepted.")

    print("Choice validation: PASS")


def test_none_validation():
    validate_not_none("value")

    try:
        validate_not_none(None)
    except ValueError:
        pass
    else:
        raise AssertionError("None should fail.")

    print("None validation: PASS")


if __name__ == "__main__":
    test_string_validation()
    test_identifier_validation()
    test_integer_validation()
    test_number_validation()
    test_url_validation()
    test_path_validation()
    test_mapping_validation()
    test_sequence_validation()
    test_choice_validation()
    test_none_validation()

    print("All utility validator tests passed.")
