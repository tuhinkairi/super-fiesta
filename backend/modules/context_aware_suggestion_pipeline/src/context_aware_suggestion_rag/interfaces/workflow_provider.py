"""
Workflow provider interfaces.

Defines a common contract for workflow execution implementations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.workflows.models import (
    WorkflowDefinition,
    WorkflowExecution,
)


class WorkflowProvider(ABC):
    """Abstract contract for workflow execution providers."""

    @abstractmethod
    def execute(
        self,
        definition: WorkflowDefinition,
        input_data: Mapping[str, Any],
        metadata: Mapping[str, Any] | None = None,
    ) -> WorkflowExecution:
        """Execute a workflow definition."""
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> bool:
        """Check whether the workflow provider is operational."""
        raise NotImplementedError

    def close(self) -> None:
        """Release provider resources when applicable."""
        return None
