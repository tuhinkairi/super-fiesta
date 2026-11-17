from graphrag_app.extraction.gemini_client import GeminiClient


def main():
    client = GeminiClient()

    response = client.generate_text(
        prompt="Explain what a knowledge graph is in two sentences."
    )

    print("\nGemini response:")
    print(response)

    assert isinstance(response, str)
    assert len(response.strip()) > 0

    print("\nLangChain Gemini test passed!")


if __name__ == "__main__":
    main()
