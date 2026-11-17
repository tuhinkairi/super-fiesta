
from context_aware_suggestion_rag.config.validation import (
    ConfigurationIssue,
    ConfigurationValidator,
    ConfigurationValidationResult,
    validate_configuration,
)


def valid_configurations():
    return {
        "embedding": {
            "dense_dimension": 768,
            "sparse_provider": "bm25",
        },
        "pinecone": {
            "dimension": 768,
            "index_name": "suggestion-index",
        },
        "retrieval": {
            "dense_weight": 0.7,
            "sparse_weight": 0.3,
            "fusion_method": "weighted_score",
            "reranking_enabled": False,
        },
    }


def test_valid_configuration():
    result = validate_configuration(valid_configurations())

    assert isinstance(result, ConfigurationValidationResult)
    assert result.is_valid
    assert result.error_count == 0


def test_dimension_mismatch():
    config = valid_configurations()
    config["pinecone"]["dimension"] = 1536

    result = validate_configuration(config)

    assert not result.is_valid
    assert any(
        "does not match" in issue.message
        for issue in result.errors
    )


def test_invalid_retrieval_weights():
    config = valid_configurations()
    config["retrieval"]["dense_weight"] = 0.8
    config["retrieval"]["sparse_weight"] = 0.3

    result = validate_configuration(config)

    assert not result.is_valid


def test_invalid_weight_type():
    config = valid_configurations()
    config["retrieval"]["dense_weight"] = float("nan")

    result = validate_configuration(config)

    assert not result.is_valid


def test_reranking_configuration():
    config = valid_configurations()
    config["retrieval"]["reranking_enabled"] = True

    result = validate_configuration(config)

    assert not result.is_valid
    assert any(
        issue.field == "reranker_provider"
        for issue in result.errors
    )


def test_valid_reranking_configuration():
    config = valid_configurations()
    config["retrieval"].update({
        "reranking_enabled": True,
        "reranker_provider": "cohere",
        "reranker_model": "rerank-model",
    })

    result = validate_configuration(config)

    assert result.is_valid


def test_invalid_fusion_method():
    config = valid_configurations()
    config["retrieval"]["fusion_method"] = "unknown"

    result = validate_configuration(config)

    assert not result.is_valid


def test_invalid_sparse_provider():
    config = valid_configurations()
    config["embedding"]["sparse_provider"] = "unknown"

    result = validate_configuration(config)

    assert not result.is_valid


def test_empty_index_name():
    config = valid_configurations()
    config["pinecone"]["index_name"] = ""

    result = validate_configuration(config)

    assert not result.is_valid


def test_validate_or_raise():
    config = valid_configurations()
    config["pinecone"]["dimension"] = 1024

    validator = ConfigurationValidator(config)

    try:
        validator.validate_or_raise()
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "Configuration validation failed" in str(exc)


def test_issue_validation():
    issue = ConfigurationIssue(
        component="pinecone",
        field="dimension",
        message="Dimension mismatch",
    )

    assert issue.severity == "error"

    try:
        ConfigurationIssue(
            component="pinecone",
            field="dimension",
            message="Invalid",
            severity="critical",
        )
        assert False, "Expected ValueError"
    except ValueError:
        pass


if __name__ == "__main__":
    tests = [
        test_valid_configuration,
        test_dimension_mismatch,
        test_invalid_retrieval_weights,
        test_invalid_weight_type,
        test_reranking_configuration,
        test_valid_reranking_configuration,
        test_invalid_fusion_method,
        test_invalid_sparse_provider,
        test_empty_index_name,
        test_validate_or_raise,
        test_issue_validation,
    ]

    for test in tests:
        test()
        print(f"{test.__name__}: PASS")

    print("All configuration validation tests passed.")
