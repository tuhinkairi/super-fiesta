"""Metadata filter utilities for vector database queries."""

from __future__ import annotations

import math
from typing import Any


SUPPORTED_OPERATORS = {
    "$eq",
    "$ne",
    "$gt",
    "$gte",
    "$lt",
    "$lte",
    "$in",
    "$nin",
    "$exists",
}


def _validate_filter_value(value: Any) -> None:
    """Validate values supported by Pinecone metadata filters."""
    if value is None:
        raise ValueError("Filter values cannot be None.")

    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("Filter values must be finite.")

    if isinstance(value, (str, int, float, bool)):
        return

    if isinstance(value, list):
        if not value:
            raise ValueError("Filter lists cannot be empty.")

        for item in value:
            if isinstance(item, (list, dict)) or item is None:
                raise ValueError(
                    "Filter lists must contain scalar values."
                )

            if isinstance(item, float) and not math.isfinite(item):
                raise ValueError("Filter values must be finite.")

            if not isinstance(item, (str, int, float, bool)):
                raise ValueError(
                    "Unsupported value inside filter list."
                )
        return

    raise ValueError(
        f"Unsupported filter value type: {type(value).__name__}"
    )


def validate_metadata_filter(
    metadata_filter: dict[str, Any],
) -> dict[str, Any]:
    """Validate a Pinecone-compatible metadata filter."""
    if not isinstance(metadata_filter, dict):
        raise TypeError("Metadata filter must be a dictionary.")

    if not metadata_filter:
        return {}

    validated: dict[str, Any] = {}

    for key, condition in metadata_filter.items():
        if key in {"$and", "$or"}:
            if not isinstance(condition, list) or not condition:
                raise ValueError(
                    f"'{key}' must contain a non-empty list."
                )

            validated[key] = [
                validate_metadata_filter(item)
                for item in condition
            ]
            continue

        if not isinstance(key, str) or not key.strip():
            raise ValueError("Filter field names must be non-empty.")

        if isinstance(condition, dict):
            if len(condition) != 1:
                raise ValueError(
                    f"Filter condition for '{key}' must contain "
                    "exactly one operator."
                )

            operator, value = next(iter(condition.items()))

            if operator not in SUPPORTED_OPERATORS:
                raise ValueError(
                    f"Unsupported filter operator: {operator}"
                )

            if operator == "$exists":
                if not isinstance(value, bool):
                    raise ValueError(
                        "'$exists' requires a boolean value."
                    )
            else:
                _validate_filter_value(value)

            validated[key] = {operator: value}
        else:
            _validate_filter_value(condition)
            validated[key] = {"$eq": condition}

    return validated


def build_metadata_filter(
    **conditions: Any,
) -> dict[str, Any]:
    """Build a metadata filter using equality conditions."""
    if not conditions:
        return {}

    return validate_metadata_filter(conditions)


def combine_filters(
    *filters: dict[str, Any],
    operator: str = "$and",
) -> dict[str, Any]:
    """Combine multiple metadata filters using AND or OR."""
    if operator not in {"$and", "$or"}:
        raise ValueError("Operator must be '$and' or '$or'.")

    if not filters:
        return {}

    validated_filters = [
        validate_metadata_filter(item)
        for item in filters
    ]

    validated_filters = [
        item for item in validated_filters if item
    ]

    if not validated_filters:
        return {}

    if len(validated_filters) == 1:
        return validated_filters[0]

    return {operator: validated_filters}
