from dataclasses import dataclass


@dataclass(frozen=True)
class ChunkingConfig:
    """Configuration for character-based document chunking."""

    chunk_size: int = 1000
    chunk_overlap: int = 150

    def __post_init__(self):
        if self.chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero.")

        if self.chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative.")

        if self.chunk_overlap >= self.chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size."
            )


class CharacterChunkingStrategy:
    """Splits text into overlapping character-based chunks."""

    def __init__(self, config: ChunkingConfig | None = None):
        self.config = config or ChunkingConfig()

    def split(self, text: str) -> list[tuple[int, int, str]]:
        """Split text into chunks.

        Returns:
            A list of (start_char, end_char, chunk_text) tuples.
        """

        if not isinstance(text, str):
            raise TypeError("Input text must be a string.")

        if not text.strip():
            raise ValueError("Cannot split empty text.")

        chunks = []

        text_length = len(text)
        start = 0

        while start < text_length:
            end = min(
                start + self.config.chunk_size,
                text_length,
            )

            chunk_text = text[start:end]

            if chunk_text.strip():
                chunks.append((start, end, chunk_text))

            if end == text_length:
                break

            start = end - self.config.chunk_overlap

        return chunks
