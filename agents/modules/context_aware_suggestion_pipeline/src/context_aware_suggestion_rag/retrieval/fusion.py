"""
Reciprocal Rank Fusion for combining retrieval results.
"""

from __future__ import annotations

from collections import defaultdict

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.exceptions import RetrievalError

from .models import RetrievedDocument


class ReciprocalRankFusion:
    """Combine ranked document lists using Reciprocal Rank Fusion."""

    def __init__(
        self,
        rrf_constant: int = 60,
        dense_weight: float = 0.5,
        sparse_weight: float = 0.5,
    ) -> None:
        if (
            not isinstance(rrf_constant, int)
            or isinstance(rrf_constant, bool)
            or rrf_constant <= 0
        ):
            raise ValueError("rrf_constant must be a positive integer.")

        if dense_weight < 0 or sparse_weight < 0:
            raise ValueError("Fusion weights cannot be negative.")

        if dense_weight + sparse_weight <= 0:
            raise ValueError("At least one fusion weight must be positive.")

        self.rrf_constant = rrf_constant

        total_weight = dense_weight + sparse_weight
        self.dense_weight = dense_weight / total_weight
        self.sparse_weight = sparse_weight / total_weight

    def fuse(
        self,
        dense_results: list[RetrievedDocument],
        sparse_results: list[RetrievedDocument],
        top_k: int = 10,
    ) -> list[RetrievedDocument]:
        """
        Combine dense and sparse rankings.

        Documents are identified by their IDs. If a document occurs in
        both lists, its reciprocal-rank contributions are added.
        """
        if (
            not isinstance(top_k, int)
            or isinstance(top_k, bool)
            or top_k <= 0
        ):
            raise ValueError("top_k must be a positive integer.")

        scores: dict[str, float] = defaultdict(float)
        documents: dict[str, RetrievedDocument] = {}

        self._accumulate(
            dense_results,
            self.dense_weight,
            scores,
            documents,
        )

        self._accumulate(
            sparse_results,
            self.sparse_weight,
            scores,
            documents,
        )

        ranked_ids = sorted(
            scores,
            key=lambda document_id: (-scores[document_id], document_id),
        )

        fused_documents: list[RetrievedDocument] = []

        for rank, document_id in enumerate(ranked_ids[:top_k], start=1):
            original = documents[document_id]

            metadata = dict(original.metadata)
            metadata["rrf_score"] = scores[document_id]

            fused_documents.append(
                RetrievedDocument(
                    id=original.id,
                    content=original.content,
                    score=scores[document_id],
                    metadata=metadata,
                    namespace=original.namespace,
                    source_type=original.source_type,
                    rank=rank,
                )
            )

        return fused_documents

    def _accumulate(
        self,
        results: list[RetrievedDocument],
        weight: float,
        scores: dict[str, float],
        documents: dict[str, RetrievedDocument],
    ) -> None:
        """Add weighted reciprocal-rank contributions."""
        if weight == 0:
            return

        for position, document in enumerate(results, start=1):
            document_id = document.id

            scores[document_id] += weight / (
                self.rrf_constant + position
            )

            # Preserve the first encountered document representation.
            documents.setdefault(document_id, document)


def reciprocal_rank_fusion(
    dense_results: list[RetrievedDocument],
    sparse_results: list[RetrievedDocument],
    top_k: int = 10,
    rrf_constant: int = 60,
    dense_weight: float = 0.5,
    sparse_weight: float = 0.5,
) -> list[RetrievedDocument]:
    """Convenience function for reciprocal rank fusion."""
    try:
        fusion = ReciprocalRankFusion(
            rrf_constant=rrf_constant,
            dense_weight=dense_weight,
            sparse_weight=sparse_weight,
        )

        return fusion.fuse(
            dense_results=dense_results,
            sparse_results=sparse_results,
            top_k=top_k,
        )

    except (ValueError, TypeError) as exc:
        raise RetrievalError(
            f"Could not fuse retrieval results: {exc}"
        ) from exc
