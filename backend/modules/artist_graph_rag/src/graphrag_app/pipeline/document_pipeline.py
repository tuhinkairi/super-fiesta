from typing import Any
from typing_extensions import TypedDict

from langgraph.graph import END, START, StateGraph

from modules.artist_graph_rag.src.graphrag_app.ingestion import (
    IngestionRequest,
    IngestionStatus,
    IngestionService,
)
from modules.artist_graph_rag.src.graphrag_app.document import DocumentService
from modules.artist_graph_rag.src.graphrag_app.chunking import ChunkingService
from modules.artist_graph_rag.src.graphrag_app.extraction import ExtractionService
from modules.artist_graph_rag.src.graphrag_app.graph import GraphIngestionService

from modules.artist_graph_rag.src.graphrag_app.pipeline.models import (
    PipelineStatus,
    DocumentPipelineResult,
)


class DocumentPipelineState(TypedDict, total=False):
    """Shared state passed between document-processing nodes."""

    request: IngestionRequest
    ingestion_result: Any
    extracted_document: Any
    chunks: list[Any]
    extractions: list[Any]

    chunks_created: int
    entities_stored: int
    relationships_stored: int

    error: str


class DocumentPipeline:
    """Coordinates document ingestion through a LangGraph workflow."""

    def __init__(
        self,
        ingestion_service: IngestionService,
        document_service: DocumentService,
        chunking_service: ChunkingService,
        extraction_service: ExtractionService,
        graph_ingestion_service: GraphIngestionService,
    ):
        self.ingestion_service = ingestion_service
        self.document_service = document_service
        self.chunking_service = chunking_service
        self.extraction_service = extraction_service
        self.graph_ingestion_service = graph_ingestion_service

        self.workflow = self._build_workflow()

    def _build_workflow(self):
        """Construct and compile the document-processing graph."""

        graph = StateGraph(DocumentPipelineState)

        graph.add_node("ingest_document", self._ingest_document)
        graph.add_node("extract_document", self._extract_document)
        graph.add_node("chunk_document", self._chunk_document)
        graph.add_node("extract_knowledge", self._extract_knowledge)
        graph.add_node("store_graph", self._store_graph)
        graph.add_node("handle_failure", self._handle_failure)

        graph.add_edge(START, "ingest_document")

        graph.add_conditional_edges(
            "ingest_document",
            self._route_after_node,
            {
                "continue": "extract_document",
                "failed": "handle_failure",
            },
        )

        graph.add_conditional_edges(
            "extract_document",
            self._route_after_node,
            {
                "continue": "chunk_document",
                "failed": "handle_failure",
            },
        )

        graph.add_conditional_edges(
            "chunk_document",
            self._route_after_node,
            {
                "continue": "extract_knowledge",
                "failed": "handle_failure",
            },
        )

        graph.add_conditional_edges(
            "extract_knowledge",
            self._route_after_node,
            {
                "continue": "store_graph",
                "failed": "handle_failure",
            },
        )

        graph.add_conditional_edges(
            "store_graph",
            self._route_after_node,
            {
                "continue": END,
                "failed": "handle_failure",
            },
        )

        graph.add_edge("handle_failure", END)

        return graph.compile()

    def _ingest_document(
        self,
        state: DocumentPipelineState,
    ) -> dict:
        """Validate and store the uploaded document."""

        try:
            request = state["request"]

            ingestion_result = self.ingestion_service.ingest(request)

            if ingestion_result.status != IngestionStatus.COMPLETED:
                raise RuntimeError(
                    ingestion_result.error or "Document ingestion failed."
                )

            return {
                "ingestion_result": ingestion_result,
            }

        except Exception as error:
            return {"error": str(error)}

    def _extract_document(
        self,
        state: DocumentPipelineState,
    ) -> dict:
        """Extract and clean document text."""

        try:
            request = state["request"]
            ingestion_result = state["ingestion_result"]

            extracted_document = self.document_service.process(
                file_path=ingestion_result.stored_path,
                document_id=request.document_id,
                filename=request.filename,
            )

            return {
                "extracted_document": extracted_document,
            }

        except Exception as error:
            return {"error": str(error)}

    def _chunk_document(
        self,
        state: DocumentPipelineState,
    ) -> dict:
        """Split the extracted document into chunks."""

        try:
            chunks = self.chunking_service.chunk_document(state["extracted_document"])

            if not chunks:
                raise RuntimeError("Document processing produced no chunks.")

            return {
                "chunks": chunks,
                "chunks_created": len(chunks),
            }

        except Exception as error:
            return {"error": str(error)}

    def _extract_knowledge(
        self,
        state: DocumentPipelineState,
    ) -> dict:
        """Extract entities and relationships from every chunk."""

        try:
            extractions = []

            for chunk in state["chunks"]:
                extraction = self.extraction_service.extract(chunk)
                extractions.append(extraction)

            return {
                "extractions": extractions,
            }

        except Exception as error:
            return {"error": str(error)}

    def _store_graph(
        self,
        state: DocumentPipelineState,
    ) -> dict:
        """Store extracted knowledge in Neo4j."""

        entities_stored = 0
        relationships_stored = 0

        try:
            for extraction in state["extractions"]:
                graph_result = self.graph_ingestion_service.store_extraction(extraction)

                entities_stored += graph_result["entities_stored"]
                relationships_stored += graph_result["relationships_stored"]

            return {
                "entities_stored": entities_stored,
                "relationships_stored": relationships_stored,
            }

        except Exception as error:
            return {
                "entities_stored": entities_stored,
                "relationships_stored": relationships_stored,
                "error": str(error),
            }

    @staticmethod
    def _route_after_node(
        state: DocumentPipelineState,
    ) -> str:
        """Route execution depending on whether a node failed."""

        if state.get("error"):
            return "failed"

        return "continue"

    @staticmethod
    def _handle_failure(
        state: DocumentPipelineState,
    ) -> dict:
        """Preserve the error in the workflow state."""

        return state

    def process(
        self,
        request: IngestionRequest,
    ) -> DocumentPipelineResult:
        """Execute the compiled LangGraph document workflow."""

        initial_state: DocumentPipelineState = {
            "request": request,
            "chunks_created": 0,
            "entities_stored": 0,
            "relationships_stored": 0,
        }

        state = self.workflow.invoke(initial_state)

        if state.get("error"):
            return DocumentPipelineResult(
                document_id=request.document_id,
                filename=request.filename,
                status=PipelineStatus.FAILED,
                chunks_created=state.get("chunks_created", 0),
                entities_stored=state.get("entities_stored", 0),
                relationships_stored=state.get("relationships_stored", 0),
                message="Document pipeline processing failed.",
                error=state["error"],
            )

        return DocumentPipelineResult(
            document_id=request.document_id,
            filename=request.filename,
            status=PipelineStatus.COMPLETED,
            chunks_created=state.get("chunks_created", 0),
            entities_stored=state.get("entities_stored", 0),
            relationships_stored=state.get("relationships_stored", 0),
            message=("Document successfully processed and " "knowledge graph stored."),
        )
