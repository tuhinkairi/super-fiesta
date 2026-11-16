import pytest
"""Integration tests for project configuration modules."""

from context_aware_suggestion_rag.config.llm_config import (
    get_llm_config,
)
from context_aware_suggestion_rag.config.pinecone_config import (
    get_pinecone_config,
)
from context_aware_suggestion_rag.config.embedding_config import (
    get_embedding_config,
)
from context_aware_suggestion_rag.config.retrieval_config import (
    get_retrieval_config,
)
from context_aware_suggestion_rag.config.trend_config import (
    get_trend_config,
)
from context_aware_suggestion_rag.config.validation import (
    ConfigurationValidator,
)


def model_fields(config):
    """Return a dictionary representation of a configuration object."""


    if hasattr(config, "model_dump"):
        return config.model_dump()

    if hasattr(config, "__dict__"):
        return vars(config)

    raise TypeError(
        f"Unsupported configuration object: {type(config).__name__}"
    )


@pytest.fixture(scope="module")
def configurations():
    """Load all project configurations for integration tests."""
    return {
        "llm": get_llm_config(),
        "pinecone": get_pinecone_config(),
        "embedding": get_embedding_config(),
        "retrieval": get_retrieval_config(),
        "trend": get_trend_config(),
    }


def test_configuration_loading(configurations):
    for name, config in configurations.items():
        assert config is not None, f"{name} configuration is missing"
        print(f"{name}: LOADED")


def test_configuration_fields(configurations):
    for name, config in configurations.items():
        fields = model_fields(config)

        assert isinstance(fields, dict)

        print(f"\n{name.upper()} CONFIGURATION FIELDS")

        for field in sorted(fields):
            value = fields[field]

            # Do not print API keys or secret values.
            if any(
                secret in field.lower()
                for secret in ("key", "secret", "password", "token")
            ):
                value = "<REDACTED>"

            print(f"  {field}: {value}")


def test_embedding_dimension_consistency(configurations):
    embedding = model_fields(configurations["embedding"])
    pinecone = model_fields(configurations["pinecone"])

    embedding_dimension = embedding.get("dense_dimension")
    index_dimension = pinecone.get("dimension")

    assert embedding_dimension is not None
    assert index_dimension is not None

    print(f"\nEmbedding dimension: {embedding_dimension}")
    print(f"Pinecone dimension: {index_dimension}")

    assert embedding_dimension == index_dimension, (
        "Embedding and Pinecone dimensions do not match."
    )


def test_cross_component_validation(configurations):
    mapped = {
        "embedding": model_fields(configurations["embedding"]),
        "pinecone": model_fields(configurations["pinecone"]),
        "retrieval": model_fields(configurations["retrieval"]),
    }

    result = ConfigurationValidator(mapped).validate()

    for issue in result.issues:
        print(
            f"{issue.severity.upper()}: "
            f"{issue.component}.{issue.field}: {issue.message}"
        )

    assert result.is_valid, "Cross-component configuration validation failed."


def test_llm_configuration(configurations):
    llm = model_fields(configurations["llm"])

    assert llm.get("provider") is not None
    assert llm.get("model_name") is not None

    print("\nLLM provider:", llm["provider"])
    print("LLM model:", llm["model_name"])

    if hasattr(configurations["llm"], "is_configured"):
        print(
            "LLM API key configured:",
            configurations["llm"].is_configured,
        )


def test_trend_configuration(configurations):
    trend = model_fields(configurations["trend"])

    assert trend

    print("\nTrend and news configuration loaded.")

    for field in sorted(trend):
        if "key" not in field.lower():
            print(f"  {field}: {trend[field]}")



if __name__ == "__main__":
    configurations = {
        "llm": get_llm_config(),
        "pinecone": get_pinecone_config(),
        "embedding": get_embedding_config(),
        "retrieval": get_retrieval_config(),
        "trend": get_trend_config(),
    }

    test_configuration_loading(configurations)
    test_configuration_fields(configurations)
    test_embedding_dimension_consistency(configurations)
    test_cross_component_validation(configurations)
    test_llm_configuration(configurations)
    test_trend_configuration(configurations)

    print("\nAll configuration integration tests passed.")
