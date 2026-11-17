
from context_aware_suggestion_rag.llm.base import BaseLLMProvider
from context_aware_suggestion_rag.llm.models import (
    LLMRequest,
    LLMResponse,
)
from context_aware_suggestion_rag.llm.service import LLMService


class FakeLLMProvider(BaseLLMProvider):

    def connect(self) -> bool:
        return True

    def health_check(self) -> bool:
        return True

    def generate(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(
            text=f"Generated response for: {request.prompt}",
            model="fake-model",
            provider="fake-provider",
        )

    def generate_many(
        self,
        requests: list[LLMRequest],
    ) -> list[LLMResponse]:
        return [
            self.generate(request)
            for request in requests
        ]


provider = FakeLLMProvider()
service = LLMService(provider)

# Health check.
assert service.health_check() is True
print("LLM service health check: PASS")

# Single generation.
request = LLMRequest(
    prompt="Explain artificial intelligence."
)

response = service.generate(request)

assert isinstance(response, LLMResponse)
assert "artificial intelligence" in response.text

print("Single LLM generation: PASS")

# Batch generation.
requests = [
    LLMRequest(prompt="Explain machine learning."),
    LLMRequest(prompt="Explain deep learning."),
]

responses = service.generate_many(requests)

assert len(responses) == 2
assert all(
    isinstance(response, LLMResponse)
    for response in responses
)

print("Batch LLM generation: PASS")

# Invalid request.
try:
    service.generate("invalid request")
except TypeError:
    print("Invalid request validation: PASS")
else:
    raise AssertionError("Invalid requests should be rejected.")

# Invalid batch request.
try:
    service.generate_many(["invalid"])
except TypeError:
    print("Invalid batch validation: PASS")
else:
    raise AssertionError("Invalid batch items should be rejected.")

# Cleanup.
service.close()

print("LLM service cleanup: PASS")
print("All LLM service tests passed.")
