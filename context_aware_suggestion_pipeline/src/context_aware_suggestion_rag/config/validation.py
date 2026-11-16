
"""Cross-component configuration validation."""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ConfigurationIssue:
    """A configuration validation issue."""

    component: str
    field: str
    message: str
    severity: str = "error"

    def __post_init__(self) -> None:
        for name in ("component", "field", "message"):
            value = getattr(self, name)

            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string.")

        if self.severity not in {"error", "warning"}:
            raise ValueError("severity must be 'error' or 'warning'.")


@dataclass(frozen=True, slots=True)
class ConfigurationValidationResult:
    """Aggregated configuration validation result."""

    issues: tuple[ConfigurationIssue, ...]

    @property
    def is_valid(self) -> bool:
        return not self.errors

    @property
    def errors(self) -> tuple[ConfigurationIssue, ...]:
        return tuple(
            issue for issue in self.issues
            if issue.severity == "error"
        )

    @property
    def warnings(self) -> tuple[ConfigurationIssue, ...]:
        return tuple(
            issue for issue in self.issues
            if issue.severity == "warning"
        )

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def warning_count(self) -> int:
        return len(self.warnings)


class ConfigurationValidator:
    """Validate configuration consistency across project components."""

    SUPPORTED_FUSION_STRATEGIES = {
        "weighted_score",
        "rrf",
        "reciprocal_rank_fusion",
    }

    SUPPORTED_SPARSE_PROVIDERS = {"bm25"}

    def __init__(
        self,
        configurations: Mapping[str, Any],
    ) -> None:
        if not isinstance(configurations, Mapping):
            raise TypeError("configurations must be a mapping.")

        self.configurations = dict(configurations)

    def _get(
        self,
        component: str,
        field: str,
        default: Any = None,
    ) -> Any:
        config = self.configurations.get(component)

        if config is None:
            return default

        if isinstance(config, Mapping):
            return config.get(field, default)

        return getattr(config, field, default)

    def _issue(
        self,
        issues: list[ConfigurationIssue],
        component: str,
        field: str,
        message: str,
        severity: str = "error",
    ) -> None:
        issues.append(
            ConfigurationIssue(
                component=component,
                field=field,
                message=message,
                severity=severity,
            )
        )

    def _validate_embedding_dimension(
        self,
        issues: list[ConfigurationIssue],
    ) -> None:
        embedding_dimension = self._get(
            "embedding", "dense_dimension"
        )
        index_dimension = self._get(
            "pinecone", "dimension"
        )

        if embedding_dimension is None or index_dimension is None:
            return

        if (
            isinstance(embedding_dimension, bool)
            or not isinstance(embedding_dimension, int)
            or embedding_dimension <= 0
        ):
            self._issue(
                issues,
                "embedding",
                "dense_dimension",
                "Dense embedding dimension must be a positive integer.",
            )
            return

        if (
            isinstance(index_dimension, bool)
            or not isinstance(index_dimension, int)
            or index_dimension <= 0
        ):
            self._issue(
                issues,
                "pinecone",
                "dimension",
                "Pinecone dimension must be a positive integer.",
            )
            return

        if embedding_dimension != index_dimension:
            self._issue(
                issues,
                "pinecone",
                "dimension",
                (
                    f"Pinecone dimension ({index_dimension}) does not match "
                    f"embedding dimension ({embedding_dimension})."
                ),
            )

    def _validate_retrieval_weights(
        self,
        issues: list[ConfigurationIssue],
    ) -> None:
        dense_weight = self._get(
            "retrieval", "dense_weight"
        )
        sparse_weight = self._get(
            "retrieval", "sparse_weight"
        )

        if dense_weight is None or sparse_weight is None:
            return

        values = (dense_weight, sparse_weight)

        if any(
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            or value < 0
            for value in values
        ):
            self._issue(
                issues,
                "retrieval",
                "dense_weight/sparse_weight",
                "Retrieval weights must be finite, non-negative numbers.",
            )
            return

        if not math.isclose(
            dense_weight + sparse_weight,
            1.0,
            rel_tol=0.0,
            abs_tol=1e-6,
        ):
            self._issue(
                issues,
                "retrieval",
                "dense_weight/sparse_weight",
                "Dense and sparse weights must sum to 1.0.",
            )

    def _validate_reranking(
        self,
        issues: list[ConfigurationIssue],
    ) -> None:
        enabled = self._get(
            "retrieval", "reranking_enabled", None
        )

        if enabled is None:
            enabled = self._get(
                "retrieval", "rerank_enabled", False
            )

        if not isinstance(enabled, bool):
            self._issue(
                issues,
                "retrieval",
                "reranking_enabled",
                "Reranking enabled must be a boolean.",
            )
            return

        if not enabled:
            return

        provider = self._get(
            "retrieval", "reranker_provider"
        )
        model = self._get(
            "retrieval", "reranker_model"
        )

        if not isinstance(provider, str) or not provider.strip():
            self._issue(
                issues,
                "retrieval",
                "reranker_provider",
                "A reranker provider is required when reranking is enabled.",
            )

        if not isinstance(model, str) or not model.strip():
            self._issue(
                issues,
                "retrieval",
                "reranker_model",
                "A reranker model is required when reranking is enabled.",
            )

    def _validate_fusion_method(
        self,
        issues: list[ConfigurationIssue],
    ) -> None:
        # The actual RetrievalConfig field is fusion_strategy.
        # fusion_method remains supported for compatibility.
        strategy = self._get(
            "retrieval", "fusion_strategy", None
        )

        field_name = "fusion_strategy"

        if strategy is None:
            strategy = self._get(
                "retrieval", "fusion_method", None
            )
            field_name = "fusion_method"

        if strategy is None:
            return

        if (
            not isinstance(strategy, str)
            or strategy.lower() not in self.SUPPORTED_FUSION_STRATEGIES
        ):
            self._issue(
                issues,
                "retrieval",
                field_name,
                (
                    f"Unsupported fusion strategy: {strategy!r}. "
                    f"Supported values: "
                    f"{', '.join(sorted(self.SUPPORTED_FUSION_STRATEGIES))}."
                ),
            )

    def _validate_sparse_provider(
        self,
        issues: list[ConfigurationIssue],
    ) -> None:
        provider = self._get(
            "embedding", "sparse_provider"
        )

        if provider is None:
            return

        if (
            not isinstance(provider, str)
            or provider.lower() not in self.SUPPORTED_SPARSE_PROVIDERS
        ):
            self._issue(
                issues,
                "embedding",
                "sparse_provider",
                f"Unsupported sparse provider: {provider!r}.",
            )

    def _validate_pinecone_index(
        self,
        issues: list[ConfigurationIssue],
    ) -> None:
        index_name = self._get(
            "pinecone", "index_name"
        )

        if index_name is None:
            return

        if not isinstance(index_name, str) or not index_name.strip():
            self._issue(
                issues,
                "pinecone",
                "index_name",
                "Pinecone index name cannot be empty.",
            )

    def validate(self) -> ConfigurationValidationResult:
        """Run all cross-component configuration checks."""

        issues: list[ConfigurationIssue] = []

        self._validate_embedding_dimension(issues)
        self._validate_retrieval_weights(issues)
        self._validate_reranking(issues)
        self._validate_fusion_method(issues)
        self._validate_sparse_provider(issues)
        self._validate_pinecone_index(issues)

        return ConfigurationValidationResult(
            issues=tuple(issues)
        )

    def validate_or_raise(self) -> ConfigurationValidationResult:
        """Validate configuration and raise on errors."""

        result = self.validate()

        if not result.is_valid:
            messages = [
                f"{issue.component}.{issue.field}: {issue.message}"
                for issue in result.errors
            ]

            raise ValueError(
                "Configuration validation failed:\n"
                + "\n".join(messages)
            )

        return result


def validate_configuration(
    configurations: Mapping[str, Any],
) -> ConfigurationValidationResult:
    """Convenience function for cross-component validation."""

    return ConfigurationValidator(configurations).validate()


__all__ = [
    "ConfigurationIssue",
    "ConfigurationValidationResult",
    "ConfigurationValidator",
    "validate_configuration",
]
