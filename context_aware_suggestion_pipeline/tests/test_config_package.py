
"""Tests for the public configuration package."""

from context_aware_suggestion_rag.config import (
    get_embedding_config,
    get_llm_config,
    get_pinecone_config,
    get_retrieval_config,
    get_trend_config,
    ConfigurationValidator,
    ConfigurationIssue,
    ConfigurationValidationResult,
    validate_configuration,
)


def test_configuration_getters():
    assert get_embedding_config() is not None
    assert get_llm_config() is not None
    assert get_pinecone_config() is not None
    assert get_retrieval_config() is not None
    assert get_trend_config() is not None


def test_validation_exports():
    assert ConfigurationValidator is not None
    assert ConfigurationIssue is not None
    assert ConfigurationValidationResult is not None
    assert callable(validate_configuration)


if __name__ == "__main__":
    test_configuration_getters()
    test_validation_exports()

    print("Configuration getters: PASS")
    print("Configuration validation exports: PASS")
    print("All configuration package tests passed.")
