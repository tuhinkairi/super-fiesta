"""
Base workflow interfaces.

Defines abstract contracts for workflow execution and management.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.core.base import BaseWorkflow
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.workflows.models import (
    WorkflowDefinition,
    WorkflowExecution,
)


class BasePipelineWorkflow(BaseWorkflow):
    """Abstract interface for executable pipeline workflows."""

    @abstractmethod
    def execute(
        self,
        input_data: dict[str, Any],
        *,
        metadata: dict[str, Any] | None = None,
    ) -> WorkflowExecution:
        raise NotImplementedError

    @abstractmethod
    def validate_input(self, input_data: dict[str, Any]) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_definition(self) -> WorkflowDefinition:
        raise NotImplementedError


class BaseWorkflowManager(ABC):
    """Abstract interface for registering and executing workflows."""

    @abstractmethod
    def register(self, workflow: BasePipelineWorkflow) -> None:
        raise NotImplementedError

    @abstractmethod
    def unregister(self, workflow_name: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get(self, workflow_name: str) -> BasePipelineWorkflow:
        raise NotImplementedError

    @abstractmethod
    def list_workflows(self) -> Sequence[str]:
        raise NotImplementedError

    @abstractmethod
    def execute(
        self,
        workflow_name: str,
        input_data: dict[str, Any],
        *,
        metadata: dict[str, Any] | None = None,
    ) -> WorkflowExecution:
        raise NotImplementedError
