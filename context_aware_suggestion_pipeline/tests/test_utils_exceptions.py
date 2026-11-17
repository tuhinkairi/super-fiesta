
from context_aware_suggestion_rag.utils.exceptions import (
    CollectionError,
    ConversionError,
    FormattingError,
    PathUtilityError,
    SerializationError,
    UtilityError,
    ValidationUtilityError,
)


def test_exception_inheritance():
    exceptions = [
        ConversionError,
        FormattingError,
        CollectionError,
        SerializationError,
        ValidationUtilityError,
        PathUtilityError,
    ]

    for exception_class in exceptions:
        assert issubclass(exception_class, UtilityError)
        assert issubclass(exception_class, Exception)


def test_exception_messages():
    error = ConversionError("Unable to convert value")

    assert str(error) == "Unable to convert value"


def test_exception_catching():
    try:
        raise SerializationError("Invalid JSON")
    except UtilityError as error:
        assert str(error) == "Invalid JSON"
    else:
        raise AssertionError("Expected UtilityError")


if __name__ == "__main__":
    tests = [
        test_exception_inheritance,
        test_exception_messages,
        test_exception_catching,
    ]

    for test in tests:
        test()
        print(f"{test.__name__}: PASS")

    print("All utility exception tests passed.")
