
from context_aware_suggestion_rag.generation.base import (
    BaseGenerationProvider,
)
from context_aware_suggestion_rag.generation.models import (
    GeneratedContent,
    GenerationRequest,
    GenerationResult,
    GenerationStatus,
)
from context_aware_suggestion_rag.generation.service import (
    GenerationService,
)


class FakeGenerationProvider(BaseGenerationProvider):

    def connect(self) -> bool:
        return True

    def health_check(self) -> bool:
        return True

    def generate(
        self,
        request: GenerationRequest,
    ) -> GenerationResult:
        content = GeneratedContent(
            request_id=request.request_id,
            content="Artificial intelligence is transforming technology.",
            content_format=request.content_format,
            model="fake-model",
            title="Artificial Intelligence",
        )

        return GenerationResult(
            request_id=request.request_id,
            status=GenerationStatus.COMPLETED,
            generated_content=content,
            model="fake-model",
        )

    def generate_many(
        self,
        requests: list[GenerationRequest],
    ) -> list[GenerationResult]:
        return [self.generate(request) for request in requests]


provider = FakeGenerationProvider()
service = GenerationService(provider)

# Health check.
assert service.health_check() is True
print("Generation service health check: PASS")

# Single generation.
request = GenerationRequest(
    prompt="Explain artificial intelligence.",
)

result = service.generate(request)

assert isinstance(result, GenerationResult)
assert result.success
assert result.generated_content is not None

print("Single generation: PASS")

# Batch generation.
requests = [
    GenerationRequest(prompt="Explain machine learning."),
    GenerationRequest(prompt="Explain deep learning."),
]

results = service.generate_many(requests)

assert len(results) == 2
assert all(result.success for result in results)

print("Batch generation: PASS")

# Content validation.
validation = service.validate_content(
    result.generated_content
)

assert validation.is_valid
print("Content validation: PASS")


# Formatting.
formatted = service.format_content(
    result.generated_content,
    "markdown",
)

assert isinstance(formatted, str)
assert "Artificial Intelligence" in formatted

print("Content formatting: PASS")


service.close()

print("All generation service tests passed.")
