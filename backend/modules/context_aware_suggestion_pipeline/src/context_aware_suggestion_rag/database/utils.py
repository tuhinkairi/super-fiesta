"""Utility functions for vector database operations."""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Any, Sequence

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.database.models import VectorRecord


def validate_dense_vector(
    vector: Sequence[float],
    expected_dimension: int | None = None,
) -> list[float]:
    """Validate and normalize a dense vector."""
    if not vector:
        raise ValueError("Dense vector cannot be empty.")

    values: list[float] = []

    for value in vector:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("Dense vector values must be numeric.")

        normalized = float(value)

        if not math.isfinite(normalized):
            raise ValueError("Dense vector values must be finite.")

        values.append(normalized)

    if expected_dimension is not None:
        if expected_dimension <= 0:
            raise ValueError("Expected dimension must be positive.")

        if len(values) != expected_dimension:
            raise ValueError(
                f"Expected {expected_dimension} dimensions, "
                f"received {len(values)}."
            )

    return values


def validate_sparse_vector(
    indices: Sequence[int],
    values: Sequence[float],
) -> tuple[list[int], list[float]]:
    """Validate and normalize a sparse vector."""
    if len(indices) != len(values):
        raise ValueError(
            "Sparse vector indices and values must have equal lengths."
        )

    if len(set(indices)) != len(indices):
        raise ValueError("Sparse vector indices must be unique.")

    normalized_indices: list[int] = []
    normalized_values: list[float] = []

    for index in indices:
        if isinstance(index, bool) or not isinstance(index, int):
            raise ValueError("Sparse vector indices must be integers.")

        if index < 0:
            raise ValueError("Sparse vector indices cannot be negative.")

        normalized_indices.append(index)

    for value in values:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("Sparse vector values must be numeric.")

        normalized = float(value)

        if not math.isfinite(normalized):
            raise ValueError("Sparse vector values must be finite.")

        normalized_values.append(normalized)

    return normalized_indices, normalized_values


def validate_vector_record(
    record: VectorRecord,
    expected_dimension: int | None = None,
) -> VectorRecord:
    """Validate a vector record."""
    if not isinstance(record, VectorRecord):
        raise TypeError("record must be a VectorRecord instance.")

    record.values = validate_dense_vector(
        record.values,
        expected_dimension=expected_dimension,
    )

    if record.sparse_indices is not None or record.sparse_values is not None:
        if record.sparse_indices is None or record.sparse_values is None:
            raise ValueError(
                "Sparse indices and values must be provided together."
            )

        (
            record.sparse_indices,
            record.sparse_values,
        ) = validate_sparse_vector(
            record.sparse_indices,
            record.sparse_values,
        )

    return record


def group_records_by_namespace(
    records: Sequence[VectorRecord],
) -> dict[str, list[VectorRecord]]:
    """Group vector records by namespace."""
    grouped: dict[str, list[VectorRecord]] = defaultdict(list)

    for record in records:
        if not isinstance(record, VectorRecord):
            raise TypeError("Every item must be a VectorRecord.")

        grouped[record.namespace].append(record)

    return dict(grouped)


def prepare_metadata(
    metadata: dict[str, Any],
) -> dict[str, Any]:
    """Return a copy of metadata after basic validation."""
    if not isinstance(metadata, dict):
        raise TypeError("Metadata must be a dictionary.")

    prepared: dict[str, Any] = {}

    for key, value in metadata.items():
        if not isinstance(key, str) or not key.strip():
            raise ValueError("Metadata keys must be non-empty strings.")

        if value is None:
            continue

        if isinstance(value, (str, int, float, bool)):
            if isinstance(value, float) and not math.isfinite(value):
                raise ValueError(
                    f"Metadata value for '{key}' must be finite."
                )
            prepared[key] = value

        elif isinstance(value, list):
            if not all(
                isinstance(item, (str, int, float, bool))
                and not isinstance(item, float)
                or isinstance(item, float) and math.isfinite(item)
                for item in value
            ):
                raise ValueError(
                    f"Metadata list '{key}' contains unsupported values."
                )
            prepared[key] = value

        else:
            raise ValueError(
                f"Unsupported metadata value type for '{key}': "
                f"{type(value).__name__}"
            )

    return prepared
