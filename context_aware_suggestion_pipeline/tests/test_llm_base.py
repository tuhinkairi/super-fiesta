
from context_aware_suggestion_rag.llm.base import (
    BaseLLMProvider,
)
from context_aware_suggestion_rag.llm.models import (
    LLMRequest,
    LLMResponse,
)


class FakeLLMProvider(BaseLLMProvider):

    def connect(self) -> bool:
        return True

    def health_check(self) -> bool:
        return True

    def generate(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(
            text="Test response",
            model="fake-model",
            provider="fake",
        )

    def generate_many(
        self,
        requests: list[LLMRequest],
    ) -> list[LLMResponse]:
        return [self.generate(request) for request in requests]


# Abstract interface test.
try:
    BaseLLMProvider()
except TypeError:
    print("Abstract LLM provider validation: PASS")
else:
    raise AssertionError(
        "BaseLLMProvider should not be instantiated."
    )


# Concrete implementation test.
provider = FakeLLMProvider()

assert provider.connect() is True
assert provider.health_check() is True

print("LLM provider connection: PASS")
print("LLM provider health check: PASS")


# Single generation.
request = LLMRequest(
    prompt="Explain artificial intelligence."
)

response = provider.generate(request)

assert isinstance(response, LLMResponse)
assert response.text == "Test response"

print("Single LLM generation: PASS")


# Batch generation.
requests = [
    LLMRequest(prompt="Explain machine learning."),
    LLMRequest(prompt="Explain deep learning."),
]

responses = provider.generate_many(requests)

assert len(responses) == 2
assert all(isinstance(item, LLMResponse) for item in responses)

print("Batch LLM generation: PASS")

print("All LLM base tests passed.")
