from modules.inspiration_ingestion.processing.chunker import TextChunker


def main():
    sample_text = (
        "Storytelling is an art of expressing ideas. "
        "Every story has characters, events, and emotions. "
        "A good story creates a connection with its audience. "
        "Creative writing allows people to explore imagination. "
    ) * 10

    chunker = TextChunker(
        chunk_size=100,
        chunk_overlap=20,
    )

    chunks = chunker.chunk_text(sample_text)

    print("Text chunking successful!")
    print("Original character count:", len(sample_text))
    print("Number of chunks:", len(chunks))

    for index, chunk in enumerate(chunks, start=1):
        print(f"\nChunk {index}:")
        print(chunk)
        print("Length:", len(chunk))

    # Validation checks.
    assert len(chunks) > 1
    assert all(chunk.strip() for chunk in chunks)
    assert all(len(chunk) <= 100 for chunk in chunks)

    # Empty input should return an empty list.
    assert chunker.chunk_text("") == []

    # Invalid configuration should be rejected.
    try:
        TextChunker(chunk_size=100, chunk_overlap=100)
        raise AssertionError("Invalid chunk configuration accepted!")
    except ValueError as error:
        print("\nInvalid configuration correctly rejected:", error)

    print("\nAll Text Chunker checks passed!")


if __name__ == "__main__":
    main()
