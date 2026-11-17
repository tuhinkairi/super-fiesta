
from context_aware_suggestion_rag.interfaces.generation_provider import (
    GenerationProvider,
)
from context_aware_suggestion_rag.generation.models import (
    GenerationRequest,
    GenerationResult,
    GenerationStatus,
)


class FakeGenerationProvider(GenerationProvider):

    def connect(self):
        pass

    def health_check(self):
        return True

    def generate(self, request):
        return GenerationResult(
            request_id=request.request_id,
            status=GenerationStatus.COMPLETED,
            model="fake-model",
        )

    def generate_many(self, requests):
        return [self.generate(request) for request in requests]


def main():
    provider = FakeGenerationProvider()

    assert isinstance(provider, GenerationProvider)
    print("Generation provider inheritance: PASS")

    provider.connect()
    assert provider.health_check()
    print("Connection and health check: PASS")

    request = GenerationRequest(
        prompt="Write about artificial intelligence."
    )

    result = provider.generate(request)

    assert isinstance(result, GenerationResult)
    assert result.status == GenerationStatus.COMPLETED
    print("Single generation interface: PASS")

    requests = [
        GenerationRequest(prompt="Explain RAG."),
        GenerationRequest(prompt="Explain machine learning."),
    ]

    results = provider.generate_many(requests)

    assert len(results) == 2
    assert all(isinstance(item, GenerationResult) for item in results)
    print("Batch generation interface: PASS")

    provider.close()
    print("Provider close interface: PASS")

    print("\nAll generation provider interface tests passed.")


if __name__ == "__main__":
    main()
