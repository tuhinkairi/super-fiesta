
from modules.inspiration_ingestion.config import (
    get_inspiration_settings,
)


class TextChunker:
    """
    Divides extracted text into overlapping chunks
    while preserving word boundaries.
    """

    def __init__(
        self,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ):
        settings = get_inspiration_settings()

        self.chunk_size = (
            chunk_size if chunk_size is not None
            else settings.chunk_size
        )

        self.chunk_overlap = (
            chunk_overlap if chunk_overlap is not None
            else settings.chunk_overlap
        )

        if self.chunk_size <= 0:
            raise ValueError("Chunk size must be positive.")

        if self.chunk_overlap < 0:
            raise ValueError("Chunk overlap cannot be negative.")

        if self.chunk_overlap >= self.chunk_size:
            raise ValueError(
                "Chunk overlap must be smaller than chunk size."
            )

    def chunk_text(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = min(start + self.chunk_size, text_length)

            if end < text_length:
                minimum_boundary = start + self.chunk_size // 2

                # Find the nearest suitable word boundary.
                space_position = text.rfind(
                    " ", minimum_boundary, end
                )
                newline_position = text.rfind(
                    "\n", minimum_boundary, end
                )

                boundary = max(space_position, newline_position)

                if boundary > start:
                    end = boundary

            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            if end >= text_length:
                break

            # Calculate the next starting position.
            next_start = end - self.chunk_overlap

            # Move backwards to a word boundary so that
            # the next chunk does not start mid-word.
            if next_start > start:
                space_position = text.rfind(
                    " ", start, next_start + 1
                )
                newline_position = text.rfind(
                    "\n", start, next_start + 1
                )

                boundary = max(space_position, newline_position)

                if boundary >= start:
                    next_start = boundary + 1

            # Safety check to prevent an infinite loop.
            if next_start <= start:
                next_start = end

            start = next_start

        return chunks
