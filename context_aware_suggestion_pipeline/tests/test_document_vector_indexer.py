
"""Tests for document-to-vector indexing integration."""

from types import SimpleNamespace

import pytest

from context_aware_suggestion_rag.database.models import (
    DatabaseOperationResult,
)
from context_aware_suggestion_rag.document_context import DocumentContextResult
from context_aware_suggestion_rag.document_vector_indexer import (
    DocumentVectorIndexer,
)
from context_aware_suggestion_rag.embeddings.models import (
    DenseEmbedding,
    SparseEmbedding,
)
from context_aware_suggestion_rag.exceptions import EmbeddingError


class FakeEmbeddingService:
    def __init__(self, results=None):
        self.results = results
        self.received_texts = None
        self.closed = False

    def embed_hybrid_batch(self, texts):
        self.received_texts = list(texts)
        if self.results is not None:
            return self.results

        return [
            (
                DenseEmbedding(values=[0.1, 0.2, 0.3], model="fake-dense"),
                SparseEmbedding(
                    indices=[1, 2],
                    values=[0.5, 0.8],
                    model="fake-sparse",
                ),
            )
            for _ in texts
        ]

    def close(self):
        self.closed = True


class FakeVectorRepository:
    def __init__(self):
        self.saved_records = None
        self.closed = False

    def save_many(self, records):
        self.saved_records = list(records)
        return DatabaseOperationResult(
            success=True,
            operation="upsert",
            affected_count=len(records),
        )

    def close(self):
        self.closed = True


def make_document_result(chunks=None):
    """Build a lightweight DocumentContextResult for integration tests."""
    result = object.__new__(DocumentContextResult)
    result.ingestion_result = SimpleNamespace(
        document_id="doc-001",
        filename="sample.txt",
    )
    result.chunks = chunks if chunks is not None else [
        SimpleNamespace(
            chunk_id="chunk-001",
            document_id="doc-001",
            content="First document chunk.",
            chunk_index=0,
        ),
        SimpleNamespace(
            chunk_id="chunk-002",
            document_id="doc-001",
            content="Second document chunk.",
            chunk_index=1,
        ),
    ]
    result.context = None
    result.analysis = None
    return result


def test_index_document_saves_hybrid_vectors():
    embedding_service = FakeEmbeddingService()
    repository = FakeVectorRepository()
    indexer = DocumentVectorIndexer(embedding_service, repository)

    result = indexer.index_document(make_document_result())

    assert result.document_id == "doc-001"
    assert result.indexed_count == 2
    assert len(result.records) == 2
    assert embedding_service.received_texts == [
        "First document chunk.",
        "Second document chunk.",
    ]
    assert len(repository.saved_records) == 2

    record = repository.saved_records[0]
    assert record.id == "chunk-001"
    assert record.namespace == "documents"
    assert record.values == [0.1, 0.2, 0.3]
    assert record.sparse_indices == [1, 2]
    assert record.sparse_values == [0.5, 0.8]
    assert record.metadata["document_id"] == "doc-001"
    assert record.metadata["text"] == "First document chunk."
    assert result.database_result.success is True


def test_empty_chunks_do_not_call_services():
    embedding_service = FakeEmbeddingService()
    repository = FakeVectorRepository()
    indexer = DocumentVectorIndexer(embedding_service, repository)

    result = indexer.index_document(make_document_result(chunks=[]))

    assert result.indexed_count == 0
    assert result.records == []
    assert result.database_result is None
    assert embedding_service.received_texts is None
    assert repository.saved_records is None


def test_rejects_chunk_from_another_document():
    repository = FakeVectorRepository()
    indexer = DocumentVectorIndexer(FakeEmbeddingService(), repository)

    chunks = [
        SimpleNamespace(
            chunk_id="chunk-001",
            document_id="different-doc",
            content="Some text.",
            chunk_index=0,
        )
    ]

    with pytest.raises(ValueError, match="different document"):
        indexer.index_document(make_document_result(chunks))


def test_rejects_empty_chunk_content():
    repository = FakeVectorRepository()
    indexer = DocumentVectorIndexer(FakeEmbeddingService(), repository)

    chunks = [
        SimpleNamespace(
            chunk_id="chunk-001",
            document_id="doc-001",
            content="   ",
            chunk_index=0,
        )
    ]

    with pytest.raises(ValueError, match="empty content"):
        indexer.index_document(make_document_result(chunks))


def test_rejects_unexpected_embedding_count():
    embedding_service = FakeEmbeddingService(results=[])
    repository = FakeVectorRepository()
    indexer = DocumentVectorIndexer(embedding_service, repository)

    with pytest.raises(EmbeddingError, match="unexpected result count"):
        indexer.index_document(make_document_result())


def test_rejects_invalid_document_result():
    indexer = DocumentVectorIndexer(
        FakeEmbeddingService(),
        FakeVectorRepository(),
    )

    with pytest.raises(TypeError, match="DocumentContextResult"):
        indexer.index_document(object())


def test_close_closes_dependencies():
    embedding_service = FakeEmbeddingService()
    repository = FakeVectorRepository()
    indexer = DocumentVectorIndexer(embedding_service, repository)

    indexer.close()

    assert embedding_service.closed is True
    assert repository.closed is True


if __name__ == "__main__":
    for test in [
        test_index_document_saves_hybrid_vectors,
        test_empty_chunks_do_not_call_services,
        test_rejects_chunk_from_another_document,
        test_rejects_empty_chunk_content,
        test_rejects_unexpected_embedding_count,
        test_rejects_invalid_document_result,
        test_close_closes_dependencies,
    ]:
        test()

    print("All document-vector-indexer integration tests passed.")
