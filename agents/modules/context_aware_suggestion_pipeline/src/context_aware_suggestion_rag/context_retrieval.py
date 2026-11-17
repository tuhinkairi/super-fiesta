"""Connect context intelligence to document retrieval."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.constants import DOCUMENT_NAMESPACE
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.context_intelligence import (
    ContextIntelligenceResult,
)
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.retrieval.models import (
    RetrievalQuery,
    RetrievalResult,
)
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.retrieval.service import RetrievalService


@dataclass
class ContextRetrievalResult:
    """Combined context-intelligence and document-retrieval result."""

    context_intelligence: ContextIntelligenceResult
    retrieval: RetrievalResult | None

    @property
    def retrieved_documents(self) -> list[Any]:
        """Return retrieved documents, or an empty list when skipped."""
        if self.retrieval is None:
            return []

        return self.retrieval.documents

    @property
    def query(self) -> str | None:
        """Return the search query used for retrieval."""
        if self.retrieval is None:
            return self.context_intelligence.search_query

        return self.retrieval.query


class ContextRetrievalProcessor:
    """Retrieve relevant document chunks using extracted context."""

    def __init__(
        self,
        retrieval_service: RetrievalService,
    ) -> None:
        if retrieval_service is None:
            raise ValueError("retrieval_service is required.")

        if not callable(getattr(retrieval_service, "retrieve", None)):
            raise TypeError(
                "retrieval_service must provide a callable retrieve method."
            )

        self.retrieval_service = retrieval_service
        self._closed = False

    def retrieve_for_context(
        self,
        context_intelligence: ContextIntelligenceResult,
        *,
        top_k: int = 10,
        namespace: str = DOCUMENT_NAMESPACE,
        use_dense: bool = True,
        use_sparse: bool = True,
        rerank: bool = False,
        metadata_filter: dict[str, Any] | None = None,
        user_id: str | None = None,
    ) -> ContextRetrievalResult:
        """Retrieve document chunks relevant to the context search query."""
        if self._closed:
            raise RuntimeError("ContextRetrievalProcessor is closed.")

        if not isinstance(context_intelligence, ContextIntelligenceResult):
            raise TypeError(
                "context_intelligence must be a ContextIntelligenceResult."
            )

        search_query = context_intelligence.search_query

        if search_query is None or not search_query.strip():
            return ContextRetrievalResult(
                context_intelligence=context_intelligence,
                retrieval=None,
            )

        query = RetrievalQuery(
            query=search_query,
            top_k=top_k,
            namespace=namespace,
            metadata_filter=metadata_filter,
            use_dense=use_dense,
            use_sparse=use_sparse,
            rerank=rerank,
            user_id=user_id,
        )

        retrieval_result = self.retrieval_service.retrieve(query)

        if not isinstance(retrieval_result, RetrievalResult):
            raise TypeError(
                "RetrievalService.retrieve() must return RetrievalResult."
            )

        return ContextRetrievalResult(
            context_intelligence=context_intelligence,
            retrieval=retrieval_result,
        )

    def close(self) -> None:
        """Close the underlying retrieval service."""
        if self._closed:
            return

        self._closed = True
        self.retrieval_service.close()
