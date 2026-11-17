"""Create and persist hybrid vectors for ingested document chunks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.constants import DOCUMENT_NAMESPACE, SOURCE_DOCUMENT
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.database.models import (
    DatabaseOperationResult,
    VectorRecord,
)
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.database.repository import VectorRepository
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.document_context import DocumentContextResult
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.embeddings.models import (
    DenseEmbedding,
    SparseEmbedding,
)
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.embeddings.service import EmbeddingService
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.exceptions import EmbeddingError


@dataclass(slots=True)
class DocumentVectorIndexingResult:
    """Result of indexing the chunks belonging to one document."""

    document_id: str
    indexed_count: int
    records: list[VectorRecord]
    database_result: DatabaseOperationResult | None


class DocumentVectorIndexer:
    """Generate hybrid embeddings and store document chunks in Pinecone."""

    def __init__(
        self,
        embedding_service: EmbeddingService | None = None,
        vector_repository: VectorRepository | None = None,
    ) -> None:
        if vector_repository is None:
            raise ValueError("A vector repository instance is required.")

        self.embedding_service = embedding_service or EmbeddingService()
        self.vector_repository = vector_repository

    def index_document(
        self,
        document_result: DocumentContextResult,
    ) -> DocumentVectorIndexingResult:
        """Embed and persist every chunk from a processed document."""
        if not isinstance(document_result, DocumentContextResult):
            raise TypeError(
                "document_result must be a DocumentContextResult instance."
            )

        document_id = document_result.ingestion_result.document_id
        if not document_id or not document_id.strip():
            raise ValueError("Document ID cannot be empty.")

        chunks = document_result.chunks
        if not chunks:
            return DocumentVectorIndexingResult(
                document_id=document_id,
                indexed_count=0,
                records=[],
                database_result=None,
            )

        texts: list[str] = []
        for chunk in chunks:
            if chunk.document_id != document_id:
                raise ValueError(
                    f"Chunk {chunk.chunk_id!r} belongs to a different document."
                )
            if not chunk.content or not chunk.content.strip():
                raise ValueError(
                    f"Chunk {chunk.chunk_id!r} has empty content."
                )
            texts.append(chunk.content)

        embeddings = self.embedding_service.embed_hybrid_batch(texts)

        if len(embeddings) != len(chunks):
            raise EmbeddingError(
                "Embedding service returned an unexpected result count."
            )

        records: list[VectorRecord] = []

        for chunk, embedding_pair in zip(chunks, embeddings):
            if (
                not isinstance(embedding_pair, tuple)
                or len(embedding_pair) != 2
            ):
                raise EmbeddingError(
                    "Each hybrid embedding must contain dense and sparse vectors."
                )

            dense, sparse = embedding_pair
            if not isinstance(dense, DenseEmbedding):
                raise EmbeddingError("Invalid dense embedding result.")
            if not isinstance(sparse, SparseEmbedding):
                raise EmbeddingError("Invalid sparse embedding result.")

            metadata: dict[str, Any] = {
                "document_id": document_id,
                "chunk_id": chunk.chunk_id,
                "chunk_index": chunk.chunk_index,
                "source_type": SOURCE_DOCUMENT,
                "text": chunk.content,
                "filename": document_result.ingestion_result.filename,
            }

            records.append(
                VectorRecord(
                    id=chunk.chunk_id,
                    values=dense.values,
                    sparse_indices=sparse.indices,
                    sparse_values=sparse.values,
                    metadata=metadata,
                    namespace=DOCUMENT_NAMESPACE,
                )
            )

        database_result = self.vector_repository.save_many(records)

        return DocumentVectorIndexingResult(
            document_id=document_id,
            indexed_count=len(records),
            records=records,
            database_result=database_result,
        )

    def close(self) -> None:
        """Close owned embedding and repository resources."""
        self.embedding_service.close()
        self.vector_repository.close()


__all__ = [
    "DocumentVectorIndexingResult",
    "DocumentVectorIndexer",
]
