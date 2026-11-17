
import pytest

from context_aware_suggestion_rag.generation.base import (
    BaseGenerationProvider,
)


class FakeGenerationProvider(BaseGenerationProvider):

    def connect(self) -> bool:
        return True

    def health_check(self) -> bool:
        return True

    def generate(self, request):
        return None

    def generate_many(self, requests):
        return None


def test_base_provider_is_abstract():
    with pytest.raises(TypeError):
        BaseGenerationProvider()


def test_concrete_provider_can_be_instantiated():
    provider = FakeGenerationProvider()

    assert isinstance(provider, BaseGenerationProvider)


def test_provider_connection():
    provider = FakeGenerationProvider()

    assert provider.connect() is True


def test_provider_health_check():
    provider = FakeGenerationProvider()

    assert provider.health_check() is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
