from modules.artist_graph_rag.src.graphrag_app.document.models import ExtractedDocument

from modules.artist_graph_rag.src.graphrag_app.chunking.models import DocumentChunk
from modules.artist_graph_rag.src.graphrag_app.chunking.strategy import (
    CharacterChunkingStrategy,
    ChunkingConfig,
)


class ChunkingService:
    """Coordinates document chunking."""

    def __init__(
        self,
        strategy: CharacterChunkingStrategy | None = None,
    ):
        self.strategy = strategy or CharacterChunkingStrategy()

    def chunk_document(
        self,
        document: ExtractedDocument,
    ) -> list[DocumentChunk]:
        """Split an extracted document into structured chunks."""

        if not document.text.strip():
            raise ValueError("Cannot chunk a document with empty text.")

        raw_chunks = self.strategy.split(document.text)

        chunks = []

        for index, (start, end, text) in enumerate(raw_chunks):
            chunks.append(
                DocumentChunk(
                    document_id=document.document_id,
                    chunk_index=index,
                    text=text,
                    start_char=start,
                    end_char=end,
                    character_count=len(text),
                    metadata={
                        "filename": document.filename,
                        "file_extension": document.metadata.get("file_extension", ""),
                    },
                )
            )

        return chunks
