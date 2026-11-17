from modules.artist_graph_rag.src.graphrag_app.database import Neo4jClient
from modules.artist_graph_rag.src.graphrag_app.ingestion import IngestionRequest
from modules.artist_graph_rag.src.graphrag_app.pipeline import (
    DocumentPipeline,
    DocumentPipelineResult,
    QAPipeline,
)
from modules.artist_graph_rag.src.graphrag_app.retrieval import (
    RetrievalRequest,
    RetrievalResult,
)
from modules.artist_graph_rag.src.graphrag_app.generation import GenerationResult


class GraphRAGApplication:
    """Main entry point for the GraphRAG application."""

    def __init__(
        self,
        document_pipeline: DocumentPipeline,
        qa_pipeline: QAPipeline,
        neo4j_client: Neo4jClient | None = None,
    ):
        self.document_pipeline = document_pipeline
        self.qa_pipeline = qa_pipeline
        self.neo4j_client = neo4j_client

    def process_document(
        self,
        request: IngestionRequest,
    ) -> DocumentPipelineResult:
        """Process a document and store its knowledge graph."""
        return self.document_pipeline.process(request)

    def ask(
        self,
        request: RetrievalRequest,
    ) -> tuple[RetrievalResult, GenerationResult]:
        """Retrieve knowledge and generate an answer."""
        return self.qa_pipeline.answer(request)

    def verify_database_connection(self) -> bool:
        """Verify the Neo4j connection."""
        if self.neo4j_client is None:
            raise RuntimeError("Neo4jClient was not provided to the application.")

        return self.neo4j_client.verify_connection()

    def close(self) -> None:
        """Close the database connection."""
        if self.neo4j_client is not None:
            self.neo4j_client.close()

    def __enter__(self) -> "GraphRAGApplication":
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:
        self.close()
