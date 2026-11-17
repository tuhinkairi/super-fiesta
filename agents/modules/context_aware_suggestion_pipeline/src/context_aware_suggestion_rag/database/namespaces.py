
"""Namespace utilities for vector database isolation."""

from __future__ import annotations

import re

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.constants import (
    DOCUMENT_NAMESPACE,
    TREND_NAMESPACE,
    NEWS_NAMESPACE,
)


class NamespaceManager:
    """Build and validate vector database namespaces."""

    DEFAULT_NAMESPACE = "default"

    ALLOWED_TYPES = {
        DOCUMENT_NAMESPACE,
        TREND_NAMESPACE,
        NEWS_NAMESPACE,
        "recommendations",
    }

    @staticmethod
    def validate_namespace(namespace: str) -> str:
        """Validate a namespace string."""
        if not isinstance(namespace, str):
            raise TypeError("Namespace must be a string.")

        namespace = namespace.strip()

        if not namespace:
            raise ValueError("Namespace cannot be empty.")

        if len(namespace) > 128:
            raise ValueError("Namespace cannot exceed 128 characters.")

        if not re.fullmatch(r"[a-zA-Z0-9_-]+", namespace):
            raise ValueError(
                "Namespace can contain only letters, numbers, "
                "underscores and hyphens."
            )

        return namespace

    @classmethod
    def build_namespace(
        cls,
        namespace_type: str,
        user_id: str | None = None,
    ) -> str:
        """Build a namespace, optionally scoped to a user."""
        if namespace_type not in cls.ALLOWED_TYPES:
            raise ValueError(
                f"Unsupported namespace type: {namespace_type}"
            )

        if user_id is None:
            return cls.validate_namespace(namespace_type)

        validated_user_id = cls.validate_namespace(user_id)

        namespace = f"{namespace_type}_{validated_user_id}"

        return cls.validate_namespace(namespace)

    @classmethod
    def document_namespace(
        cls,
        user_id: str | None = None,
    ) -> str:
        return cls.build_namespace(DOCUMENT_NAMESPACE, user_id)

    @classmethod
    def trend_namespace(
        cls,
        user_id: str | None = None,
    ) -> str:
        return cls.build_namespace(TREND_NAMESPACE, user_id)

    @classmethod
    def news_namespace(
        cls,
        user_id: str | None = None,
    ) -> str:
        return cls.build_namespace(NEWS_NAMESPACE, user_id)
