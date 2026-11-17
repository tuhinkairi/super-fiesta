"""Reusable utilities for working with Python collections."""

from collections import defaultdict
from collections.abc import Callable, Iterable, Mapping, Sequence
from typing import Any, TypeVar

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


def group_by(
    items: Iterable[T],
    key: Callable[[T], K],
) -> dict[K, list[T]]:
    """Group items by a key returned from a callable."""
    if not callable(key):
        raise TypeError("key must be callable")

    grouped: dict[K, list[T]] = defaultdict(list)

    for item in items:
        grouped[key(item)].append(item)

    return dict(grouped)


def partition(
    items: Iterable[T],
    predicate: Callable[[T], bool],
) -> tuple[list[T], list[T]]:
    """Split items into matching and non-matching lists."""
    if not callable(predicate):
        raise TypeError("predicate must be callable")

    matched: list[T] = []
    unmatched: list[T] = []

    for item in items:
        if predicate(item):
            matched.append(item)
        else:
            unmatched.append(item)

    return matched, unmatched


def chunked(
    items: Iterable[T],
    chunk_size: int,
) -> list[list[T]]:
    """Split an iterable into lists containing at most chunk_size items."""
    if isinstance(chunk_size, bool) or not isinstance(chunk_size, int):
        raise TypeError("chunk_size must be an integer")

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")

    result: list[list[T]] = []
    current: list[T] = []

    for item in items:
        current.append(item)

        if len(current) == chunk_size:
            result.append(current)
            current = []

    if current:
        result.append(current)

    return result


def unique_by(
    items: Iterable[T],
    key: Callable[[T], K],
) -> list[T]:
    """Remove duplicates using a derived key, preserving input order."""
    if not callable(key):
        raise TypeError("key must be callable")

    seen: set[K] = set()
    result: list[T] = []

    for item in items:
        item_key = key(item)

        if item_key not in seen:
            seen.add(item_key)
            result.append(item)

    return result


def index_by(
    items: Iterable[T],
    key: Callable[[T], K],
) -> dict[K, T]:
    """Create a dictionary indexed by a derived key.

    If multiple items produce the same key, the last item wins.
    """
    if not callable(key):
        raise TypeError("key must be callable")

    return {key(item): item for item in items}


def merge_sequences(
    *sequences: Iterable[T],
    unique: bool = False,
) -> list[T]:
    """Merge multiple iterables into a single list."""
    merged: list[T] = []

    for sequence in sequences:
        merged.extend(sequence)

    if unique:
        return list(dict.fromkeys(merged))

    return merged


def flatten_one_level(
    items: Iterable[Iterable[T]],
) -> list[T]:
    """Flatten an iterable by exactly one nesting level."""
    result: list[T] = []

    for group in items:
        result.extend(group)

    return result


def dict_from_pairs(
    pairs: Iterable[tuple[K, V]],
) -> dict[K, V]:
    """Create a dictionary from key-value pairs."""
    result: dict[K, V] = {}

    for pair in pairs:
        if not isinstance(pair, tuple) or len(pair) != 2:
            raise ValueError("Each item must be a two-element tuple")

        key, value = pair
        result[key] = value

    return result


def filter_mapping(
    mapping: Mapping[K, V],
    predicate: Callable[[K, V], bool],
) -> dict[K, V]:
    """Return mapping entries that satisfy a key-value predicate."""
    if not isinstance(mapping, Mapping):
        raise TypeError("mapping must implement Mapping")

    if not callable(predicate):
        raise TypeError("predicate must be callable")

    return {
        key: value
        for key, value in mapping.items()
        if predicate(key, value)
    }


def invert_mapping(
    mapping: Mapping[K, V],
) -> dict[V, K]:
    """Invert a mapping.

    Values must be hashable. If values repeat, the last key wins.
    """
    if not isinstance(mapping, Mapping):
        raise TypeError("mapping must implement Mapping")

    return {value: key for key, value in mapping.items()}


def ensure_list(value: Any) -> list[Any]:
    """Convert a value into a list without splitting strings."""
    if value is None:
        return []

    if isinstance(value, list):
        return value.copy()

    if isinstance(value, (str, bytes, bytearray)):
        return [value]

    if isinstance(value, Iterable):
        return list(value)

    return [value]
