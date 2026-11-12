from graphrag_app.application import GraphRAGApplication

from graphrag_app.database import Neo4jClient

from graphrag_app.ingestion import (
    DocumentStorage,
    DocumentValidator,
    IngestionService,
)

from graphrag_app.document import DocumentService
from graphrag_app.chunking import ChunkingService

from graphrag_app.extraction import (
    GeminiClient,
    EntityExtractor,
    RelationshipExtractor,
    ExtractionService,
)

from graphrag_app.graph import (
    GraphService,
    GraphMapper,
    GraphIngestionService,
)

from graphrag_app.retrieval import (
    GraphRetriever,
    RetrievalService,
)

from graphrag_app.generation import AnswerGenerator

from graphrag_app.pipeline import (
    DocumentPipeline,
    QAPipeline,
)


def create_application() -> GraphRAGApplication:
    """Construct and wire all GraphRAG application services."""

    # 1. Infrastructure clients
    neo4j_client = Neo4jClient()
    gemini_client = GeminiClient()

    # 2. Document ingestion
    document_storage = DocumentStorage()
    document_validator = DocumentValidator()

    ingestion_service = IngestionService(
        validator=document_validator,
        storage=document_storage,
    )

    # 3. Document processing
    document_service = DocumentService()
    chunking_service = ChunkingService()

    # 4. Knowledge extraction
    entity_extractor = EntityExtractor(gemini_client)
    relationship_extractor = RelationshipExtractor(gemini_client)

    extraction_service = ExtractionService(
        entity_extractor=entity_extractor,
        relationship_extractor=relationship_extractor,
    )

    # 5. Knowledge graph storage
    graph_service = GraphService(neo4j_client)
    graph_mapper = GraphMapper()

    graph_ingestion_service = GraphIngestionService(
        graph_service=graph_service,
        mapper=graph_mapper,
    )

    # 6. Document pipeline
    document_pipeline = DocumentPipeline(
        ingestion_service=ingestion_service,
        document_service=document_service,
        chunking_service=chunking_service,
        extraction_service=extraction_service,
        graph_ingestion_service=graph_ingestion_service,
    )

    # 7. Retrieval
    graph_retriever = GraphRetriever(neo4j_client)
    retrieval_service = RetrievalService(graph_retriever)

    # 8. Answer generation
    answer_generator = AnswerGenerator(gemini_client)

    qa_pipeline = QAPipeline(
        retrieval_service=retrieval_service,
        answer_generator=answer_generator,
    )

    # 9. Main application
    return GraphRAGApplication(
        document_pipeline=document_pipeline,
        qa_pipeline=qa_pipeline,
        neo4j_client=neo4j_client,
    )
