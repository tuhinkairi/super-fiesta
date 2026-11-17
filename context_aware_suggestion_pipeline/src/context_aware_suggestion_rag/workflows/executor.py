"""
Workflow executor.

Coordinates workflow definitions, execution engine,
validation, and shared workflow state.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from context_aware_suggestion_rag.workflows.engine import (
    WorkflowEngine,
    WorkflowStepCallable,
)
from context_aware_suggestion_rag.workflows.models import (
    WorkflowDefinition,
    WorkflowExecution,
    WorkflowExecutionStatus,
)
from context_aware_suggestion_rag.workflows.state import WorkflowState
from context_aware_suggestion_rag.workflows.validators import (
    WorkflowValidator,
)


class WorkflowExecutor:
    """Executes workflow definitions using registered operations."""

    def __init__(
        self,
        engine: WorkflowEngine | None = None,
        validator: WorkflowValidator | None = None,
    ) -> None:
        self.engine = engine or WorkflowEngine()
        self.validator = validator or WorkflowValidator()

    def register_step(
        self,
        name: str,
        operation: WorkflowStepCallable,
    ) -> None:
        """Register an operation with the underlying engine."""
        self.engine.register_step(name, operation)

    def execute(
        self,
        definition: WorkflowDefinition,
        input_data: dict[str, Any],
        *,
        metadata: dict[str, Any] | None = None,
    ) -> WorkflowExecution:
        """Execute all steps defined by a workflow."""

        self.validator.validate_definition(definition)

        self.validator.validate_input(input_data)

        if not definition.enabled:
            raise ValueError(
                f"Workflow '{definition.name}' is disabled."
            )

        self.validator.validate_step_sequence(
            definition.steps,
            {
                name: name
                for name in self.engine.get_registered_steps()
            },
        )

        state = WorkflowState(input_data)

        execution = self.engine.execute(
            workflow_name=definition.name,
            step_names=definition.steps,
            input_data=state.snapshot(),
            metadata=metadata,
        )

        if execution.status == WorkflowExecutionStatus.FAILED:
            if execution.error:
                state.add_error(execution.error)

        state.update(execution.output_data)

        execution.metadata["state_version"] = state.version
        execution.metadata["state_errors"] = list(
            state.get_errors()
        )

        return execution

    def execute_many(
        self,
        definitions: list[WorkflowDefinition],
        input_data: dict[str, Any],
        *,
        metadata: dict[str, Any] | None = None,
    ) -> list[WorkflowExecution]:
        """Execute multiple workflow definitions independently."""

        if not isinstance(definitions, list):
            raise TypeError("Definitions must be provided as a list.")

        if not isinstance(input_data, dict):
            raise TypeError("Workflow input must be a dictionary.")

        if metadata is not None and not isinstance(metadata, dict):
            raise TypeError("Metadata must be a dictionary.")

        results: list[WorkflowExecution] = []

        for definition in definitions:
            results.append(
                self.execute(
                    definition,
                    dict(input_data),
                    metadata=dict(metadata or {}),
                )
            )

        return results


def create_workflow_executor(
    *,
    steps: Mapping[str, WorkflowStepCallable] | None = None,
) -> WorkflowExecutor:
    """Create a workflow executor with optional registered steps."""

    engine = WorkflowEngine(steps=steps)

    return WorkflowExecutor(engine=engine)
