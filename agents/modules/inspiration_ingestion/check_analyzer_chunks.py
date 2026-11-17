
from modules.inspiration_ingestion.processing.analyzer import (
    InspirationAnalyzer,
)

from modules.inspiration_ingestion.processing.chunker import (
    TextChunker,
)


# Fake AI client: no Gemini API calls.
class FakeLLMClient:

    def __init__(self):
        self.call_count = 0

    def generate_structured(self, prompt, response_schema):

        self.call_count += 1

        return response_schema(
            summary=f"Summary from chunk {self.call_count}.",
            description=f"Description from chunk {self.call_count}.",
            keywords=[
                "creativity",
                "friendship",
                f"topic{self.call_count}",
            ],
            themes=[
                "Adventure",
                f"Theme{self.call_count}",
            ],
            mood_tags=[
                "Hopeful",
                f"Mood{self.call_count}",
            ],
        )


def main():

    fake_client = FakeLLMClient()

    # Small chunk size makes it easy to test multiple chunks.
    chunker = TextChunker(
        chunk_size=100,
        chunk_overlap=20,
    )

    analyzer = InspirationAnalyzer(
        llm_client=fake_client,
        chunker=chunker,
    )

    # Generate a long sample document.
    long_text = (
        "Creativity and friendship help people discover "
        "new possibilities and overcome difficult challenges. "
    ) * 15

    chunks = chunker.chunk_text(long_text)

    print("Generated chunks:", len(chunks))

    assert len(chunks) > 1

    # Analyze the complete document.
    result = analyzer.analyze_text(long_text)

    # Verify one AI request per chunk.
    assert fake_client.call_count == len(chunks)

    print("AI analysis calls:", fake_client.call_count)
    print("Chunk processing passed.")

    # Verify combined summaries and descriptions.
    assert "Summary from chunk 1." in result.summary
    assert "Summary from chunk 2." in result.summary
    assert "Description from chunk 1." in result.description

    print("Summary combination passed.")
    print("Description combination passed.")

    # Verify duplicate removal.
    assert result.keywords.count("creativity") == 1
    assert result.themes.count("Adventure") == 1
    assert result.mood_tags.count("Hopeful") == 1

    print("Duplicate removal passed.")

    # Verify unique values from different chunks are preserved.
    assert f"topic{fake_client.call_count}" in result.keywords
    assert f"Theme{fake_client.call_count}" in result.themes
    assert f"Mood{fake_client.call_count}" in result.mood_tags

    print("Unique metadata preservation passed.")

    # Verify empty input rejection.
    try:
        analyzer.analyze_text("   ")
        raise AssertionError("Empty text was accepted.")
    except ValueError:
        print("Empty input validation passed.")

    print("\nAll chunk-aware analyzer checks passed!")


if __name__ == "__main__":
    main()
