
from context_aware_suggestion_rag.utils.collections import (
    chunked,
    dict_from_pairs,
    ensure_list,
    filter_mapping,
    flatten_one_level,
    group_by,
    index_by,
    invert_mapping,
    merge_sequences,
    partition,
    unique_by,
)


def test_group_by():
    result = group_by(
        ["apple", "apricot", "banana"],
        key=lambda item: item[0],
    )
    assert result == {
        "a": ["apple", "apricot"],
        "b": ["banana"],
    }


def test_partition():
    matched, unmatched = partition(
        [1, 2, 3, 4],
        predicate=lambda value: value % 2 == 0,
    )
    assert matched == [2, 4]
    assert unmatched == [1, 3]


def test_chunked():
    assert chunked([1, 2, 3, 4, 5], 2) == [
        [1, 2],
        [3, 4],
        [5],
    ]


def test_chunked_invalid_size():
    try:
        chunked([1, 2], 0)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")


def test_unique_by():
    items = [
        {"id": 1, "name": "A"},
        {"id": 2, "name": "B"},
        {"id": 1, "name": "C"},
    ]

    result = unique_by(items, key=lambda item: item["id"])

    assert len(result) == 2
    assert result[0]["name"] == "A"


def test_index_by():
    items = [
        {"id": 1, "name": "A"},
        {"id": 2, "name": "B"},
    ]

    result = index_by(items, key=lambda item: item["id"])

    assert result[1]["name"] == "A"
    assert result[2]["name"] == "B"


def test_merge_sequences():
    assert merge_sequences([1, 2], [2, 3]) == [1, 2, 2, 3]
    assert merge_sequences([1, 2], [2, 3], unique=True) == [1, 2, 3]


def test_flatten_one_level():
    assert flatten_one_level([[1, 2], [3], [4, 5]]) == [
        1, 2, 3, 4, 5
    ]


def test_dict_from_pairs():
    assert dict_from_pairs([("a", 1), ("b", 2)]) == {
        "a": 1,
        "b": 2,
    }


def test_filter_mapping():
    result = filter_mapping(
        {"a": 1, "b": 2, "c": 3},
        lambda key, value: value > 1,
    )
    assert result == {"b": 2, "c": 3}


def test_invert_mapping():
    assert invert_mapping({"a": 1, "b": 2}) == {
        1: "a",
        2: "b",
    }


def test_ensure_list():
    assert ensure_list(None) == []
    assert ensure_list("hello") == ["hello"]
    assert ensure_list([1, 2]) == [1, 2]
    assert ensure_list((1, 2)) == [1, 2]
    assert ensure_list(10) == [10]


if __name__ == "__main__":
    tests = [
        test_group_by,
        test_partition,
        test_chunked,
        test_chunked_invalid_size,
        test_unique_by,
        test_index_by,
        test_merge_sequences,
        test_flatten_one_level,
        test_dict_from_pairs,
        test_filter_mapping,
        test_invert_mapping,
        test_ensure_list,
    ]

    for test in tests:
        test()
        print(f"{test.__name__}: PASS")

    print("All collection utility tests passed.")
