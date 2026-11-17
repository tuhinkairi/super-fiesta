"""Data models for retrieval operations."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def current_utc_time() -> datetime:
    """Return the current UTC timestamp."""
    return datetime.now(timezone.utc)


@dataclass
class RetrievalQuery:
    """Represents a query submitted to the retrieval system."""

    query: str
    top_k: int = 10
    namespace: str = "documents"
    metadata_filter: dict[str, Any] | None = None
    use_dense: bool = True
    use_sparse: bool = True
    rerank: bool = False
    user_id: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.query, str) or not self.query.strip():
            raise ValueError("Query cannot be empty.")

        self.query = self.query.strip()

        if isinstance(self.top_k, bool) or not isinstance(self.top_k, int):
            raise TypeError("top_k must be an integer.")

        if self.top_k <= 0:
            raise ValueError("top_k must be greater than zero.")

        if not self.namespace or not self.namespace.strip():
            raise ValueError("Namespace cannot be empty.")

        if not self.use_dense and not self.use_sparse:
            raise ValueError(
                "At least one retrieval method must be enabled."
            )

        if self.metadata_filter is not None:
            if not isinstance(self.metadata_filter, dict):
                raise TypeError("metadata_filter must be a dictionary.")

        if self.user_id is not None:
            if not isinstance(self.user_id, str) or not self.user_id.strip():
                raise ValueError("user_id cannot be empty.")


@dataclass
class RetrievedDocument:
    """Represents one document returned by retrieval."""

    id: str
    content: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)
    namespace: str = "documents"
    source_type: str = "document"
    rank: int | None = None

    def __post_init__(self) -> None:
        if not self.id or not self.id.strip():
            raise ValueError("Document ID cannot be empty.")

        if not isinstance(self.content, str):
            raise TypeError("Document content must be a string.")

        if isinstance(self.score, bool) or not isinstance(
            self.score, (int, float)
        ):
            raise TypeError("Document score must be numeric.")

        if not isinstance(self.metadata, dict):
            raise TypeError("Metadata must be a dictionary.")

        if not self.namespace or not self.namespace.strip():
            raise ValueError("Namespace cannot be empty.")


@dataclass
class RetrievalResult:
    """Contains the results of a retrieval operation."""

    query: str
    documents: list[RetrievedDocument] = field(default_factory=list)
    total_matches: int = 0
    retrieval_method: str = "dense"
    execution_time_ms: float = 0.0
    retrieved_at: datetime = field(default_factory=current_utc_time)
    warnings: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.total_matches == 0 and self.documents:
            self.total_matches = len(self.documents)

        if self.total_matches < 0:
            raise ValueError("total_matches cannot be negative.")

        if self.execution_time_ms < 0:
            raise ValueError("Execution time cannot be negative.")

    @property
    def is_empty(self) -> bool:
        return len(self.documents) == 0

    @property
    def best_match(self) -> RetrievedDocument | None:
        if not self.documents:
            return None

        return max(self.documents, key=lambda document: document.score)


@dataclass
class HybridRetrievalResult(RetrievalResult):
    """Contains dense and sparse retrieval information."""

    dense_results: list[RetrievedDocument] = field(default_factory=list)
    sparse_results: list[RetrievedDocument] = field(default_factory=list)
    fusion_method: str = "weighted_score"


@dataclass
class RetrievalMetrics:
    """Metrics collected during retrieval."""

    query_count: int = 0
    total_documents_retrieved: int = 0
    average_execution_time_ms: float = 0.0
    empty_result_count: int = 0
    failed_query_count: int = 0

    def record(
        self,
        result: RetrievalResult,
    ) -> None:
        """Update metrics using a retrieval result."""
        previous_count = self.query_count

        self.query_count += 1
        self.total_documents_retrieved += len(result.documents)

        self.average_execution_time_ms = (
            self.average_execution_time_ms * previous_count
            + result.execution_time_ms
        ) / self.query_count

        if result.is_empty:
            self.empty_result_count += 1
