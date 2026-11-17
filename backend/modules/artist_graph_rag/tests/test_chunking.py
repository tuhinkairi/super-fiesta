from pathlib import Path

import pytest

from graphrag_app.document.models import ExtractedDocument
from graphrag_app.chunking import (
    ChunkingConfig,
    CharacterChunkingStrategy,
    ChunkingService,
)


def create_document(text: str) -> ExtractedDocument:
    """Create a sample extracted document for testing."""

    return ExtractedDocument(
        document_id="test-document-001",
        filename="research.txt",
        text=text,
        character_count=len(text),
        metadata={
            "file_extension": ".txt",
            "file_size_bytes": len(text),
        },
    )


def test_chunking_config():
    """Test valid chunking configuration."""

    config = ChunkingConfig(
        chunk_size=100,
        chunk_overlap=20,
    )

    assert config.chunk_size == 100
    assert config.chunk_overlap == 20


def test_invalid_chunking_config():
    """Test invalid chunking configuration."""

    with pytest.raises(ValueError):
        ChunkingConfig(chunk_size=100, chunk_overlap=100)

    with pytest.raises(ValueError):
        ChunkingConfig(chunk_size=100, chunk_overlap=-1)


def test_character_chunking():
    """Test character-based splitting and overlap."""

    text = "A" * 250

    strategy = CharacterChunkingStrategy(
        ChunkingConfig(
            chunk_size=100,
            chunk_overlap=20,
        )
    )

    chunks = strategy.split(text)

    assert len(chunks) == 3

    assert chunks[0] == (0, 100, "A" * 100)
    assert chunks[1] == (80, 180, "A" * 100)
    assert chunks[2] == (160, 250, "A" * 90)


def test_short_text_creates_one_chunk():
    """Test that text shorter than chunk size creates one chunk."""

    text = "GraphRAG combines graphs and retrieval."

    strategy = CharacterChunkingStrategy(
        ChunkingConfig(chunk_size=100, chunk_overlap=20)
    )

    chunks = strategy.split(text)

    assert len(chunks) == 1
    assert chunks[0][0] == 0
    assert chunks[0][1] == len(text)
    assert chunks[0][2] == text


def test_empty_text_rejected():
    """Test that empty text cannot be chunked."""

    strategy = CharacterChunkingStrategy()

    with pytest.raises(ValueError):
        strategy.split("")

    with pytest.raises(ValueError):
        strategy.split("   ")


def test_chunking_service():
    """Test conversion of an extracted document into chunks."""

    text = "Machine Learning " * 100
    document = create_document(text)

    service = ChunkingService(
        CharacterChunkingStrategy(
            ChunkingConfig(
                chunk_size=200,
                chunk_overlap=40,
            )
        )
    )

    chunks = service.chunk_document(document)

    assert len(chunks) > 1

    for index, chunk in enumerate(chunks):
        assert chunk.document_id == document.document_id
        assert chunk.chunk_index == index
        assert chunk.character_count == len(chunk.text)
        assert chunk.start_char < chunk.end_char
        assert chunk.text == text[
            chunk.start_char:chunk.end_char
        ]


def test_chunk_positions_preserve_original_text():
    """Test that chunk positions map back to the source text."""

    text = "Artificial Intelligence and Knowledge Graphs"
    document = create_document(text)

    service = ChunkingService(
        CharacterChunkingStrategy(
            ChunkingConfig(
                chunk_size=15,
                chunk_overlap=5,
            )
        )
    )

    chunks = service.chunk_document(document)

    for chunk in chunks:
        original_text = text[
            chunk.start_char:chunk.end_char
        ]

        assert original_text == chunk.text


def test_chunk_metadata():
    """Test that document metadata is passed to each chunk."""

    document = create_document("GraphRAG is useful.")

    service = ChunkingService()
    chunks = service.chunk_document(document)

    assert len(chunks) == 1
    assert chunks[0].metadata["filename"] == "research.txt"
    assert chunks[0].metadata["file_extension"] == ".txt"
