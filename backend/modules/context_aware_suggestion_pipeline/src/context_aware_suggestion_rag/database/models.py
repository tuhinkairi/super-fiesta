"""Data models for vector database operations."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def current_utc_time() -> datetime:
    """Return the current UTC time."""
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class VectorRecord:
    """Represents a vector record prepared for database storage."""

    id: str
    values: list[float]
    metadata: dict[str, Any] = field(default_factory=dict)
    sparse_indices: list[int] | None = None
    sparse_values: list[float] | None = None
    namespace: str = "documents"

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("Vector record ID cannot be empty.")

        if not self.values:
            raise ValueError("Dense vector values cannot be empty.")

        if any(not isinstance(value, (int, float)) for value in self.values):
            raise TypeError("Dense vector values must be numeric.")

        self.values = [float(value) for value in self.values]

        if (self.sparse_indices is None) != (self.sparse_values is None):
            raise ValueError(
                "Sparse indices and values must either both be provided "
                "or both be omitted."
            )

        if self.sparse_indices is not None:
            if len(self.sparse_indices) != len(self.sparse_values or []):
                raise ValueError(
                    "Sparse indices and values must have equal lengths."
                )

            if any(
                not isinstance(index, int)
                or isinstance(index, bool)
                or index < 0
                for index in self.sparse_indices
            ):
                raise ValueError(
                    "Sparse indices must be non-negative integers."
                )

            if any(
                not isinstance(value, (int, float))
                for value in self.sparse_values or []
            ):
                raise TypeError("Sparse values must be numeric.")

            if len(set(self.sparse_indices)) != len(self.sparse_indices):
                raise ValueError("Sparse indices must be unique.")

            self.sparse_values = [
                float(value) for value in self.sparse_values or []
            ]

        if not self.namespace.strip():
            raise ValueError("Namespace cannot be empty.")

        if not isinstance(self.metadata, dict):
            raise TypeError("Metadata must be a dictionary.")


@dataclass(slots=True)
class VectorSearchResult:
    """Represents a single vector search result."""

    id: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)
    values: list[float] | None = None


@dataclass(slots=True)
class VectorQueryResult:
    """Represents the result of a vector database query."""

    matches: list[VectorSearchResult] = field(default_factory=list)
    namespace: str = "documents"
    query_time_ms: float = 0.0
    total_matches: int = 0

    def __post_init__(self) -> None:
        if self.total_matches == 0:
            self.total_matches = len(self.matches)


@dataclass(slots=True)
class DatabaseOperationResult:
    """Represents the outcome of a database operation."""

    success: bool
    operation: str
    affected_count: int = 0
    message: str = ""
    timestamp: datetime = field(default_factory=current_utc_time)
    metadata: dict[str, Any] = field(default_factory=dict)
