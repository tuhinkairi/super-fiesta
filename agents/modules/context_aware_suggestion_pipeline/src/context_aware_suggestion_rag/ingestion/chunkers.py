"""
Document chunking utilities.

Splits extracted document text into smaller overlapping chunks
for embedding generation and vector database storage.
"""

from dataclasses import dataclass

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.core.identifiers import generate_chunk_id
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.core.text import normalize_text
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.domain.entities import DocumentChunkEntity
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.exceptions import ChunkingError


@dataclass(frozen=True, slots=True)
class ChunkingConfig:
    """Configuration for document chunking."""

    chunk_size: int = 1000
    chunk_overlap: int = 150
    minimum_chunk_size: int = 100

    def __post_init__(self) -> None:
        if self.chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero.")

        if self.chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative.")

        if self.chunk_overlap >= self.chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size."
            )

        if self.minimum_chunk_size < 0:
            raise ValueError(
                "minimum_chunk_size cannot be negative."
            )

        if self.minimum_chunk_size > self.chunk_size:
            raise ValueError(
                "minimum_chunk_size cannot exceed chunk_size."
            )


class DocumentChunker:
    """Splits document text into overlapping chunks."""

    def __init__(
        self,
        config: ChunkingConfig | None = None,
    ) -> None:
        self.config = config or ChunkingConfig()

    def chunk_text(
        self,
        text: str,
        document_id: str,
    ) -> list[DocumentChunkEntity]:
        """
        Split text into overlapping document chunks.

        Args:
            text: Extracted document text.
            document_id: Identifier of the source document.

        Returns:
            A list of DocumentChunkEntity objects.

        Raises:
            ChunkingError: If chunking fails.
        """

        if not isinstance(text, str):
            raise ChunkingError("Document text must be a string.")

        if not document_id or not document_id.strip():
            raise ChunkingError("document_id cannot be empty.")

        normalized_text = normalize_text(text)

        if not normalized_text.strip():
            raise ChunkingError("Cannot chunk empty document text.")

        try:
            chunks = self._split_text(normalized_text)

            result: list[DocumentChunkEntity] = []

            for index, chunk_content in enumerate(chunks):
                result.append(
                    DocumentChunkEntity(
                        chunk_id=generate_chunk_id(),
                        document_id=document_id,
                        content=chunk_content,
                        chunk_index=index,
                        metadata={
                            "chunk_size": len(chunk_content),
                            "chunking_strategy": "character_overlap",
                        },
                    )
                )

            return result

        except ChunkingError:
            raise

        except Exception as exc:
            raise ChunkingError(
                f"Failed to chunk document '{document_id}': {exc}"
            ) from exc

    def _split_text(self, text: str) -> list[str]:
        """Split text using character-based windows with overlap."""

        chunk_size = self.config.chunk_size
        overlap = self.config.chunk_overlap
        minimum_size = self.config.minimum_chunk_size

        chunks: list[str] = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = min(start + chunk_size, text_length)

            # Prefer a nearby paragraph or sentence boundary.
            if end < text_length:
                boundary = text.rfind("\n\n", start, end)

                if boundary == -1:
                    boundary = text.rfind(". ", start, end)

                if boundary > start + minimum_size:
                    end = boundary + 1

            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            if end >= text_length:
                break

            next_start = end - overlap

            if next_start <= start:
                raise ChunkingError(
                    "Chunking failed to advance through the document."
                )

            start = next_start

        return chunks


def chunk_document(
    text: str,
    document_id: str,
    config: ChunkingConfig | None = None,
) -> list[DocumentChunkEntity]:
    """Convenience function for chunking a document."""

    return DocumentChunker(config).chunk_text(text, document_id)


__all__ = [
    "ChunkingConfig",
    "DocumentChunker",
    "chunk_document",
]
