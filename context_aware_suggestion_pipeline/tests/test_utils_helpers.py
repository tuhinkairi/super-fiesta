
from datetime import datetime
from pathlib import Path

from context_aware_suggestion_rag.utils.helpers import (
    deep_copy,
    safe_get,
    nested_get,
    nested_set,
    flatten_dict,
    chunk_sequence,
    unique_preserve_order,
    merge_dicts,
    to_json,
    from_json,
    slugify,
    truncate_text,
    get_type_name,
    is_iterable,
)


def test_deep_copy():
    original = {"items": [1, 2]}
    copied = deep_copy(original)

    copied["items"].append(3)

    assert original["items"] == [1, 2]
    print("Deep copy: PASS")


def test_safe_get():
    assert safe_get({"name": "RAG"}, "name") == "RAG"
    assert safe_get({}, "missing", "default") == "default"
    print("Safe dictionary access: PASS")


def test_nested_operations():
    data = {"user": {"profile": {"name": "Alex"}}}

    assert nested_get(data, "user.profile.name") == "Alex"

    nested_set(data, "user.profile.age", 25)

    assert nested_get(data, "user.profile.age") == 25
    print("Nested dictionary operations: PASS")


def test_flatten_dict():
    data = {"user": {"name": "Alex", "age": 25}}

    result = flatten_dict(data)

    assert result == {
        "user.name": "Alex",
        "user.age": 25,
    }
    print("Dictionary flattening: PASS")


def test_chunk_sequence():
    result = chunk_sequence([1, 2, 3, 4, 5], 2)

    assert result == [[1, 2], [3, 4], [5]]
    print("Sequence chunking: PASS")


def test_unique_preserve_order():
    result = unique_preserve_order([1, 2, 1, 3, 2])

    assert result == [1, 2, 3]
    print("Unique items: PASS")


def test_merge_dicts():
    first = {"user": {"name": "Alex", "age": 20}}
    second = {"user": {"age": 25, "city": "Kolkata"}}

    result = merge_dicts(first, second, deep=True)

    assert result["user"] == {
        "name": "Alex",
        "age": 25,
        "city": "Kolkata",
    }
    print("Dictionary merging: PASS")


def test_json_helpers():
    data = {
        "name": "RAG",
        "created": datetime(2026, 1, 1),
        "path": Path("data"),
    }

    serialized = to_json(data)
    restored = from_json(serialized)

    assert restored["name"] == "RAG"
    assert restored["created"] == "2026-01-01T00:00:00"
    assert restored["path"] == "data"
    print("JSON helpers: PASS")


def test_slugify():
    assert slugify("Context Aware Suggestion RAG!") == (
        "context-aware-suggestion-rag"
    )
    print("Slug generation: PASS")


def test_truncate_text():
    assert truncate_text("Hello World", 8) == "Hello..."
    assert truncate_text("Hello", 10) == "Hello"
    print("Text truncation: PASS")


def test_type_and_iterable_helpers():
    assert get_type_name(10) == "builtins.int"
    assert is_iterable([1, 2, 3])
    assert not is_iterable("hello")
    assert is_iterable("hello", include_strings=True)
    assert not is_iterable(10)
    print("Type and iterable helpers: PASS")


if __name__ == "__main__":
    test_deep_copy()
    test_safe_get()
    test_nested_operations()
    test_flatten_dict()
    test_chunk_sequence()
    test_unique_preserve_order()
    test_merge_dicts()
    test_json_helpers()
    test_slugify()
    test_truncate_text()
    test_type_and_iterable_helpers()

    print("All utility helper tests passed.")
