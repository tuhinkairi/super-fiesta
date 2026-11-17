
from context_aware_suggestion_rag.generation.llm_adapter import (
    LLMGenerationAdapter,
)
from context_aware_suggestion_rag.generation.models import (
    GenerationRequest,
    GenerationStatus,
)
from context_aware_suggestion_rag.llm.base import BaseLLMProvider
from context_aware_suggestion_rag.llm.models import (
    LLMRequest,
    LLMResponse,
    LLMUsage,
)
from context_aware_suggestion_rag.llm.service import LLMService


class FakeLLMProvider(BaseLLMProvider):

    def connect(self) -> bool:
        return True

    def health_check(self) -> bool:
        return True

    def generate(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(
            text="Artificial intelligence is transforming technology.",
            model="fake-model",
            provider="fake-provider",
            usage=LLMUsage(
                prompt_tokens=20,
                completion_tokens=10,
            ),
        )

    def generate_many(self, requests):
        return [self.generate(request) for request in requests]


llm_service = LLMService(FakeLLMProvider())
adapter = LLMGenerationAdapter(llm_service)

# Connection and health check.
assert adapter.connect() is True
assert adapter.health_check() is True

print("Adapter connection: PASS")
print("Adapter health check: PASS")

# Single generation.
request = GenerationRequest(
    prompt="Explain artificial intelligence.",
)

result = adapter.generate(request)

assert result.status == GenerationStatus.COMPLETED
assert result.generated_content is not None
assert result.generated_content.content
assert result.generated_content.model == "fake-model"

print("Single content generation: PASS")

# Token metadata.
metadata = result.generated_content.metadata

assert metadata["total_tokens"] == 30
assert metadata["provider"] == "fake-provider"

print("LLM response metadata mapping: PASS")

# Batch generation.
requests = [
    GenerationRequest(prompt="Explain machine learning."),
    GenerationRequest(prompt="Explain deep learning."),
]

results = adapter.generate_many(requests)

assert len(results) == 2
assert all(
    item.status == GenerationStatus.COMPLETED
    for item in results
)

print("Batch content generation: PASS")

adapter.close()

print("Adapter cleanup: PASS")
print("All generation LLM adapter tests passed.")
