"""
Workflow manager.

Maintains registered workflows and delegates execution
to the appropriate workflow implementation.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from context_aware_suggestion_rag.exceptions import WorkflowError
from context_aware_suggestion_rag.workflows.base import (
    BasePipelineWorkflow,
    BaseWorkflowManager,
)
from context_aware_suggestion_rag.workflows.models import (
    WorkflowExecution,
    WorkflowExecutionStatus,
)


class WorkflowManager(BaseWorkflowManager):
    """Registers, retrieves, and executes pipeline workflows."""

    def __init__(self) -> None:
        self._workflows: dict[str, BasePipelineWorkflow] = {}

    def register(self, workflow: BasePipelineWorkflow) -> None:
        """Register a workflow implementation."""

        if not isinstance(workflow, BasePipelineWorkflow):
            raise TypeError(
                "Workflow must implement BasePipelineWorkflow."
            )

        definition = workflow.get_definition()
        workflow_name = definition.name.strip()

        if not definition.enabled:
            raise WorkflowError(
                f"Cannot register disabled workflow '{workflow_name}'."
            )

        if workflow_name in self._workflows:
            raise WorkflowError(
                f"Workflow '{workflow_name}' is already registered."
            )

        self._workflows[workflow_name] = workflow

    def unregister(self, workflow_name: str) -> bool:
        """Remove a registered workflow."""

        normalized_name = self._validate_name(workflow_name)

        return self._workflows.pop(normalized_name, None) is not None

    def get(self, workflow_name: str) -> BasePipelineWorkflow:
        """Retrieve a workflow by name."""

        normalized_name = self._validate_name(workflow_name)

        workflow = self._workflows.get(normalized_name)

        if workflow is None:
            raise WorkflowError(
                f"Workflow '{normalized_name}' is not registered."
            )

        return workflow

    def list_workflows(self) -> Sequence[str]:
        """Return registered workflow names."""

        return tuple(self._workflows.keys())

    def execute(
        self,
        workflow_name: str,
        input_data: dict[str, Any],
        *,
        metadata: dict[str, Any] | None = None,
    ) -> WorkflowExecution:
        """Execute a registered workflow."""

        workflow = self.get(workflow_name)

        try:
            workflow.validate_input(input_data)

            execution = workflow.execute(
                input_data,
                metadata=metadata,
            )

            if not isinstance(execution, WorkflowExecution):
                raise TypeError(
                    "Workflow execute() must return WorkflowExecution."
                )

            return execution

        except Exception as exc:
            if isinstance(exc, WorkflowError):
                raise

            failed_execution = WorkflowExecution(
                workflow_name=workflow_name.strip(),
                input_data=dict(input_data),
                metadata=dict(metadata or {}),
                status=WorkflowExecutionStatus.FAILED,
                error=str(exc),
            )

            return failed_execution

    @staticmethod
    def _validate_name(workflow_name: str) -> str:
        """Validate and normalize a workflow name."""

        if not isinstance(workflow_name, str):
            raise TypeError("Workflow name must be a string.")

        normalized_name = workflow_name.strip()

        if not normalized_name:
            raise ValueError("Workflow name cannot be empty.")

        return normalized_name
