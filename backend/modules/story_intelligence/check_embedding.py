from unittest.mock import MagicMock, patch

from modules.story_intelligence.llm.llm_client import LLMClient


def main():

    # Create an LLMClient without initializing Gemini.
    llm = LLMClient.__new__(LLMClient)

    # Prepare a fake embedding response.
    fake_embedding = MagicMock()
    fake_embedding.values = [0.12, -0.34, 0.56, 0.78]

    fake_response = MagicMock()
    fake_response.embeddings = [fake_embedding]

    mock_client = MagicMock()
    mock_client.models.embed_content.return_value = fake_response

    llm.client = mock_client

    # Mock the SDK configuration object.
    with patch(
        "modules.story_intelligence.llm.llm_client.genai_types.EmbedContentConfig",
        return_value="mock embedding config",
    ):

        result = llm.generate_embedding("A lonely astronaut searching for home.")

    print("Embedding generated successfully!")

    print("Embedding:", result)
    print("Vector dimensions:", len(result))

    # Verify the returned vector.
    assert result == [0.12, -0.34, 0.56, 0.78]
    assert all(isinstance(value, float) for value in result)

    # Verify the Gemini embedding method was called.
    mock_client.models.embed_content.assert_called_once()

    print("\nGemini embedding request correctly executed.")

    # Verify empty input is rejected.
    try:
        llm.generate_embedding("")

        raise AssertionError("Empty text should have been rejected.")

    except ValueError:
        print("Empty input correctly rejected.")

    print("\nAll Embedding checks passed!")


if __name__ == "__main__":
    main()
