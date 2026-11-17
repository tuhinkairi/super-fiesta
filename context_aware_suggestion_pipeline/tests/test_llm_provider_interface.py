
from context_aware_suggestion_rag.interfaces.llm_provider import (
    LLMProvider,
)
from context_aware_suggestion_rag.llm.models import (
    LLMRequest,
    LLMResponse,
)


class FakeLLMProvider(LLMProvider):

    def connect(self):
        pass

    def health_check(self):
        return True

    def generate(self, request):
        return LLMResponse(
            text=f"Generated: {request.prompt}",
            model="fake-model",
            provider="fake",
        )

    def generate_many(self, requests):
        return [self.generate(request) for request in requests]


def main():
    provider = FakeLLMProvider()

    assert isinstance(provider, LLMProvider)
    print("LLM provider inheritance: PASS")

    provider.connect()
    assert provider.health_check()
    print("Connection and health check: PASS")

    request = LLMRequest(prompt="Explain RAG.")

    response = provider.generate(request)

    assert isinstance(response, LLMResponse)
    assert response.text == "Generated: Explain RAG."
    print("Single generation interface: PASS")

    requests = [
        LLMRequest(prompt="Explain AI."),
        LLMRequest(prompt="Explain ML."),
    ]

    responses = provider.generate_many(requests)

    assert len(responses) == 2
    assert all(isinstance(item, LLMResponse) for item in responses)
    print("Batch generation interface: PASS")

    provider.close()
    print("Provider close interface: PASS")

    print("\nAll LLM provider interface tests passed.")


if __name__ == "__main__":
    main()
