
from context_aware_suggestion_rag.generation.base import (
    BaseGenerationProvider,
)
from context_aware_suggestion_rag.generation.factory import (
    create_generation_service,
)
from context_aware_suggestion_rag.generation.formatter import (
    ContentFormatter,
)
from context_aware_suggestion_rag.generation.service import (
    GenerationService,
)
from context_aware_suggestion_rag.generation.validators import (
    GeneratedContentValidator,
)


class FakeGenerationProvider(BaseGenerationProvider):

    def connect(self) -> bool:
        return True

    def health_check(self) -> bool:
        return True

    def generate(self, request):
        raise NotImplementedError

    def generate_many(self, requests):
        raise NotImplementedError


provider = FakeGenerationProvider()

# Default factory creation.
service = create_generation_service(provider)

assert isinstance(service, GenerationService)
assert service.provider is provider

print("Default generation service factory: PASS")

# Custom component injection.
validator = GeneratedContentValidator()
formatter = ContentFormatter()

custom_service = create_generation_service(
    provider,
    validator=validator,
    formatter=formatter,
)

assert custom_service.validator is validator
assert custom_service.formatter is formatter

print("Custom component injection: PASS")

# Invalid provider validation.
try:
    create_generation_service(object())
except TypeError:
    print("Invalid provider validation: PASS")
else:
    raise AssertionError("Invalid provider should be rejected.")

print("All generation factory tests passed.")
