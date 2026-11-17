
from unittest.mock import patch

from context_aware_suggestion_rag.llm.base import BaseLLMProvider
from context_aware_suggestion_rag.llm.factory import (
    create_llm_provider,
    create_llm_service,
)
from context_aware_suggestion_rag.llm.gemini import GeminiProvider
from context_aware_suggestion_rag.llm.service import LLMService


# Test Gemini provider creation.
with patch(
    "context_aware_suggestion_rag.llm.factory.get_llm_config"
) as mock_config:
    mock_config.return_value.provider = "gemini"

    with patch(
        "context_aware_suggestion_rag.llm.factory.GeminiProvider"
    ) as mock_gemini:
        mock_gemini.return_value = GeminiProvider.__new__(
            GeminiProvider
        )

        provider = create_llm_provider()

        assert isinstance(provider, BaseLLMProvider)
        mock_gemini.assert_called_once()

print("Gemini provider factory: PASS")


# Test explicit provider selection.
with patch(
    "context_aware_suggestion_rag.llm.factory.get_llm_config"
) as mock_config:
    mock_config.return_value.provider = "unused"

    with patch(
        "context_aware_suggestion_rag.llm.factory.GeminiProvider"
    ) as mock_gemini:
        mock_gemini.return_value = GeminiProvider.__new__(
            GeminiProvider
        )

        provider = create_llm_provider("google")

        assert isinstance(provider, BaseLLMProvider)

print("Explicit provider selection: PASS")


# Test unsupported provider.
try:
    create_llm_provider("unsupported-provider")
except ValueError:
    print("Unsupported provider validation: PASS")
else:
    raise AssertionError(
        "Unsupported providers should be rejected."
    )


# Test service creation with injected provider.
class FakeProvider(BaseLLMProvider):

    def connect(self) -> bool:
        return True

    def health_check(self) -> bool:
        return True

    def generate(self, request):
        raise NotImplementedError

    def generate_many(self, requests):
        raise NotImplementedError


fake_provider = FakeProvider()

service = create_llm_service(
    provider=fake_provider
)

assert isinstance(service, LLMService)
assert service.provider is fake_provider

print("Custom LLM service factory: PASS")

print("All LLM factory tests passed.")

