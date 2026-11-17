
"""Tests for context and intelligence integration."""

from context_aware_suggestion_rag.context.models import (
    ExtractedContext,
    Topic,
    Keyword,
    NamedEntity,
)
from context_aware_suggestion_rag.context_intelligence import (
    ContextIntelligenceProcessor,
)
from context_aware_suggestion_rag.intelligence.models import (
    IntelligenceCollectionResult,
)


class FakeIntelligenceService:
    def __init__(self):
        self.received_arguments = None
        self.closed = False

    def collect(self, **kwargs):
        self.received_arguments = kwargs

        return IntelligenceCollectionResult(
            provider="fake_provider",
            collection_type="combined",
            success=True,
        )

    def close(self):
        self.closed = True


def create_context():
    return ExtractedContext(
        document_id="doc_test_001",
        topics=[
            Topic(name="Artificial Intelligence"),
            Topic(name="Cybersecurity"),
        ],
        keywords=[
            Keyword(text="Machine Learning"),
            Keyword(text="Artificial Intelligence"),
            Keyword(text="RAG"),
        ],
        entities=[
            NamedEntity(
                text="Google",
                entity_type="ORGANIZATION",
            ),
        ],
        language="en",
        region="IN",
    )


def test_build_search_query():
    service = FakeIntelligenceService()
    processor = ContextIntelligenceProcessor(
        intelligence_service=service,
    )

    query = processor.build_search_query(create_context())

    assert query == (
        "Artificial Intelligence Cybersecurity "
        "Machine Learning RAG Google"
    )


def test_duplicate_terms_are_removed():
    service = FakeIntelligenceService()
    processor = ContextIntelligenceProcessor(
        intelligence_service=service,
    )

    query = processor.build_search_query(create_context())

    assert query.count("Artificial Intelligence") == 1


def test_query_term_limit():
    service = FakeIntelligenceService()
    processor = ContextIntelligenceProcessor(
        intelligence_service=service,
        max_query_terms=2,
    )

    query = processor.build_search_query(create_context())

    assert query == "Artificial Intelligence Cybersecurity"


def test_collect_for_context():
    service = FakeIntelligenceService()
    processor = ContextIntelligenceProcessor(
        intelligence_service=service,
    )

    context = create_context()
    result = processor.collect_for_context(context)

    assert result.context is context
    assert result.search_query is not None
    assert result.intelligence.success is True

    arguments = service.received_arguments

    assert arguments["region"] == "IN"
    assert arguments["language"] == "en"
    assert arguments["query"] == result.search_query
    assert arguments["trend_limit"] == 20
    assert arguments["news_limit"] == 30


def test_custom_collection_limits():
    service = FakeIntelligenceService()
    processor = ContextIntelligenceProcessor(
        intelligence_service=service,
    )

    processor.collect_for_context(
        create_context(),
        trend_limit=10,
        news_limit=15,
    )

    assert service.received_arguments["trend_limit"] == 10
    assert service.received_arguments["news_limit"] == 15


def test_empty_context():
    service = FakeIntelligenceService()
    processor = ContextIntelligenceProcessor(
        intelligence_service=service,
    )

    context = ExtractedContext(
        document_id="doc_empty",
    )

    result = processor.collect_for_context(context)

    assert result.search_query is None
    assert service.received_arguments["query"] is None


def test_invalid_context():
    service = FakeIntelligenceService()
    processor = ContextIntelligenceProcessor(
        intelligence_service=service,
    )

    try:
        processor.collect_for_context("invalid")
    except TypeError:
        pass
    else:
        raise AssertionError("Expected TypeError")


def test_invalid_query_limit():
    try:
        ContextIntelligenceProcessor(max_query_terms=0)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")


def test_close():
    service = FakeIntelligenceService()
    processor = ContextIntelligenceProcessor(
        intelligence_service=service,
    )

    processor.close()

    assert service.closed is True


if __name__ == "__main__":
    tests = [
        test_build_search_query,
        test_duplicate_terms_are_removed,
        test_query_term_limit,
        test_collect_for_context,
        test_custom_collection_limits,
        test_empty_context,
        test_invalid_context,
        test_invalid_query_limit,
        test_close,
    ]

    for test in tests:
        test()
        print(f"{test.__name__}: PASS")

    print("\nAll context-intelligence integration tests passed.")
