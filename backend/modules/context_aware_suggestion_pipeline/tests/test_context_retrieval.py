
"""Tests for context-to-retrieval integration."""

from context_aware_suggestion_rag.context_intelligence import (
    ContextIntelligenceResult,
)
from context_aware_suggestion_rag.context_retrieval import (
    ContextRetrievalProcessor,
)
from context_aware_suggestion_rag.intelligence.models import (
    IntelligenceCollectionResult,
)
from context_aware_suggestion_rag.retrieval.models import (
    RetrievedDocument,
    RetrievalResult,
)


class FakeRetrievalService:
    def __init__(self):
        self.received_query = None
        self.close_called = False

    def retrieve(self, query):
        self.received_query = query

        return RetrievalResult(
            query=query.query,
            documents=[
                RetrievedDocument(
                    id="chunk-1",
                    content="Relevant document content.",
                    score=0.95,
                    metadata={"document_id": "doc-1"},
                )
            ],
        )

    def close(self):
        self.close_called = True


def make_context_intelligence(search_query="machine learning"):
    return ContextIntelligenceResult(
        context=None,
        intelligence=object(),
        search_query=search_query,
    )


def test_retrieves_documents():
    service = FakeRetrievalService()
    processor = ContextRetrievalProcessor(service)

    result = processor.retrieve_for_context(
        make_context_intelligence()
    )

    assert result.retrieval is not None
    assert len(result.retrieved_documents) == 1
    assert result.retrieved_documents[0].id == "chunk-1"
    assert result.query == "machine learning"


def test_passes_retrieval_options():
    service = FakeRetrievalService()
    processor = ContextRetrievalProcessor(service)

    processor.retrieve_for_context(
        make_context_intelligence("cybersecurity"),
        top_k=5,
        namespace="documents",
        use_dense=True,
        use_sparse=False,
        rerank=True,
        metadata_filter={"document_id": "doc-1"},
        user_id="user-1",
    )

    query = service.received_query

    assert query.query == "cybersecurity"
    assert query.top_k == 5
    assert query.namespace == "documents"
    assert query.use_dense is True
    assert query.use_sparse is False
    assert query.rerank is True
    assert query.metadata_filter == {"document_id": "doc-1"}
    assert query.user_id == "user-1"


def test_skips_retrieval_without_search_query():
    service = FakeRetrievalService()
    processor = ContextRetrievalProcessor(service)

    result = processor.retrieve_for_context(
        make_context_intelligence(None)
    )

    assert result.retrieval is None
    assert result.retrieved_documents == []
    assert service.received_query is None


def test_skips_retrieval_with_blank_search_query():
    service = FakeRetrievalService()
    processor = ContextRetrievalProcessor(service)

    result = processor.retrieve_for_context(
        make_context_intelligence("   ")
    )

    assert result.retrieval is None
    assert service.received_query is None


def test_rejects_invalid_context_intelligence():
    processor = ContextRetrievalProcessor(FakeRetrievalService())

    try:
        processor.retrieve_for_context(None)
    except TypeError:
        pass
    else:
        raise AssertionError("Expected TypeError.")


def test_rejects_invalid_top_k():
    processor = ContextRetrievalProcessor(FakeRetrievalService())

    try:
        processor.retrieve_for_context(
            make_context_intelligence(),
            top_k=0,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError.")


def test_close_delegates_to_retrieval_service():
    service = FakeRetrievalService()
    processor = ContextRetrievalProcessor(service)

    processor.close()

    assert service.close_called is True

    try:
        processor.retrieve_for_context(make_context_intelligence())
    except RuntimeError:
        pass
    else:
        raise AssertionError("Expected RuntimeError after close.")


def test_close_is_idempotent():
    service = FakeRetrievalService()
    processor = ContextRetrievalProcessor(service)

    processor.close()
    processor.close()

    assert service.close_called is True


if __name__ == "__main__":
    test_retrieves_documents()
    test_passes_retrieval_options()
    test_skips_retrieval_without_search_query()
    test_skips_retrieval_with_blank_search_query()
    test_rejects_invalid_context_intelligence()
    test_rejects_invalid_top_k()
    test_close_delegates_to_retrieval_service()
    test_close_is_idempotent()

    print("All context-retrieval integration tests passed.")
