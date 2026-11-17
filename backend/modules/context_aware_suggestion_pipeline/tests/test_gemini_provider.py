
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from context_aware_suggestion_rag.llm.gemini import (
    GeminiProvider,
)
from context_aware_suggestion_rag.llm.models import (
    LLMRequest,
    LLMResponse,
)


# Mock configuration.
fake_config = SimpleNamespace(
    api_key=SimpleNamespace(
        get_secret_value=lambda: "fake-test-key"
    ),
    model="test-gemini-model",
)

with patch(
    "context_aware_suggestion_rag.llm.gemini.get_llm_config",
    return_value=fake_config,
):
    provider = GeminiProvider()

    # Mock Gemini client.
    fake_response = SimpleNamespace(
        text="Gemini test response",
        usage_metadata=SimpleNamespace(
            prompt_token_count=20,
            candidates_token_count=30,
            total_token_count=50,
        ),
        candidates=[
            SimpleNamespace(
                finish_reason="STOP",
            )
        ],
    )

    fake_client = MagicMock()
    fake_client.models.generate_content.return_value = fake_response

    provider._client = fake_client

    # Single generation.
    request = LLMRequest(
        prompt="Explain retrieval augmented generation."
    )

    response = provider.generate(request)

    assert isinstance(response, LLMResponse)
    assert response.text == "Gemini test response"
    assert response.model == "test-gemini-model"
    assert response.usage.total_tokens == 50

    print("Gemini single generation: PASS")

    # Verify API configuration.
    fake_client.models.generate_content.assert_called_once()

    print("Gemini generation configuration: PASS")

    # Batch generation.
    requests = [
        LLMRequest(prompt="Explain machine learning."),
        LLMRequest(prompt="Explain deep learning."),
    ]

    responses = provider.generate_many(requests)

    assert len(responses) == 2
    assert all(isinstance(item, LLMResponse) for item in responses)

    print("Gemini batch generation: PASS")

    # Close.
    provider.close()

    assert provider._client is None

    print("Gemini client cleanup: PASS")

print("All Gemini provider tests passed.")
