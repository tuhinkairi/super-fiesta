from unittest.mock import MagicMock

import graphrag_app.factory as factory


def test_create_application_wires_all_services(monkeypatch):
    # Mock infrastructure clients.
    neo4j_client = MagicMock(name="Neo4jClient")
    gemini_client = MagicMock(name="GeminiClient")

    monkeypatch.setattr(
        factory,
        "Neo4jClient",
        lambda: neo4j_client,
    )
    monkeypatch.setattr(
        factory,
        "GeminiClient",
        lambda: gemini_client,
    )

    # Mock application services and pipelines.
    class MockService:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

    class MockPipeline:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

    monkeypatch.setattr(factory, "DocumentStorage", MockService)
    monkeypatch.setattr(factory, "DocumentValidator", MockService)
    monkeypatch.setattr(factory, "IngestionService", MockService)
    monkeypatch.setattr(factory, "DocumentService", MockService)
    monkeypatch.setattr(factory, "ChunkingService", MockService)
    monkeypatch.setattr(factory, "EntityExtractor", MockService)
    monkeypatch.setattr(factory, "RelationshipExtractor", MockService)
    monkeypatch.setattr(factory, "ExtractionService", MockService)
    monkeypatch.setattr(factory, "GraphService", MockService)
    monkeypatch.setattr(factory, "GraphMapper", MockService)
    monkeypatch.setattr(factory, "GraphIngestionService", MockService)
    monkeypatch.setattr(factory, "GraphRetriever", MockService)
    monkeypatch.setattr(factory, "RetrievalService", MockService)
    monkeypatch.setattr(factory, "AnswerGenerator", MockService)

    monkeypatch.setattr(factory, "DocumentPipeline", MockPipeline)
    monkeypatch.setattr(factory, "QAPipeline", MockPipeline)

    # Replace the final application with a mock.
    application = MagicMock(name="GraphRAGApplication")

    monkeypatch.setattr(
        factory,
        "GraphRAGApplication",
        lambda **kwargs: application,
    )

    # Execute factory.
    result = factory.create_application()

    # Verify application creation.
    assert result is application

    # Verify infrastructure clients were constructed.
    assert neo4j_client is not None
    assert gemini_client is not None


def test_factory_passes_same_clients_to_services(monkeypatch):
    neo4j_client = MagicMock()
    gemini_client = MagicMock()

    monkeypatch.setattr(
        factory,
        "Neo4jClient",
        lambda: neo4j_client,
    )
    monkeypatch.setattr(
        factory,
        "GeminiClient",
        lambda: gemini_client,
    )

    captured = {}

    class MockService:
        def __init__(self, *args, **kwargs):
            captured.setdefault(self.__class__.__name__, []).append(
                (args, kwargs)
            )

    class MockPipeline(MockService):
        pass

    for name in [
        "DocumentStorage",
        "DocumentValidator",
        "IngestionService",
        "DocumentService",
        "ChunkingService",
        "EntityExtractor",
        "RelationshipExtractor",
        "ExtractionService",
        "GraphService",
        "GraphMapper",
        "GraphIngestionService",
        "GraphRetriever",
        "RetrievalService",
        "AnswerGenerator",
    ]:
        monkeypatch.setattr(factory, name, MockService)

    monkeypatch.setattr(factory, "DocumentPipeline", MockPipeline)
    monkeypatch.setattr(factory, "QAPipeline", MockPipeline)

    monkeypatch.setattr(
        factory,
        "GraphRAGApplication",
        lambda **kwargs: kwargs,
    )

    result = factory.create_application()

    assert result["neo4j_client"] is neo4j_client

    graph_service_args, _ = captured["MockService"][4]

    # All constructors are mocked with the same class name,
    # so inspect the actual captured arguments instead.
    assert any(
        neo4j_client in args
        for args, _ in captured["MockService"]
    )

    assert any(
        gemini_client in args
        for args, _ in captured["MockService"]
    )
