
from graphrag_app.extraction.models import ChunkExtractionResult
from graphrag_app.graph.graph_service import GraphService
from graphrag_app.graph.mapper import GraphMapper


class GraphIngestionService:
    """Coordinates mapping and storage of extracted knowledge."""

    def __init__(
        self,
        graph_service: GraphService,
        mapper: GraphMapper | None = None,
    ):
        self.graph_service = graph_service
        self.mapper = mapper or GraphMapper()

    def store_extraction(
        self,
        extraction: ChunkExtractionResult,
    ) -> dict[str, int]:
        """Map an extraction result and store it in Neo4j."""

        if not extraction.document_id.strip():
            raise ValueError("Document ID cannot be empty.")

        if not extraction.chunk_id.strip():
            raise ValueError("Chunk ID cannot be empty.")

        entities, relationships = self.mapper.map_extraction(
            extraction
        )

        return self.graph_service.store_graph(
            entities=entities,
            relationships=relationships,
        )
