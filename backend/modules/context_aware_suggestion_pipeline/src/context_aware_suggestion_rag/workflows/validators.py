"""
Workflow validation utilities.

Validates workflow definitions, execution records,
step configurations, and input data.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.workflows.models import (
    WorkflowDefinition,
    WorkflowExecution,
    WorkflowExecutionStatus,
    WorkflowStep,
    WorkflowStepStatus,
)


class WorkflowValidationError(ValueError):
    """Raised when workflow validation fails."""


class WorkflowValidator:
    """Validates workflow-related models and input data."""

    def validate_definition(
        self,
        definition: WorkflowDefinition,
    ) -> None:
        """Validate a workflow definition."""

        if not isinstance(definition, WorkflowDefinition):
            raise WorkflowValidationError(
                "Expected a WorkflowDefinition instance."
            )

        if not definition.name.strip():
            raise WorkflowValidationError(
                "Workflow name cannot be empty."
            )

        if len(definition.steps) != len(set(definition.steps)):
            raise WorkflowValidationError(
                "Workflow step names must be unique."
            )

        if any(not step.strip() for step in definition.steps):
            raise WorkflowValidationError(
                "Workflow contains an empty step name."
            )

    def validate_execution(
        self,
        execution: WorkflowExecution,
    ) -> None:
        """Validate a workflow execution record."""

        if not isinstance(execution, WorkflowExecution):
            raise WorkflowValidationError(
                "Expected a WorkflowExecution instance."
            )

        if not execution.workflow_name.strip():
            raise WorkflowValidationError(
                "Execution workflow name cannot be empty."
            )

        if execution.execution_time_ms < 0:
            raise WorkflowValidationError(
                "Execution time cannot be negative."
            )

        step_names = [step.name for step in execution.steps]

        if len(step_names) != len(set(step_names)):
            raise WorkflowValidationError(
                "Execution contains duplicate step names."
            )

        if (
            execution.status == WorkflowExecutionStatus.COMPLETED
            and execution.failed_steps > 0
        ):
            raise WorkflowValidationError(
                "Completed execution cannot contain failed steps."
            )

        if (
            execution.status == WorkflowExecutionStatus.FAILED
            and not execution.error
            and execution.failed_steps == 0
        ):
            raise WorkflowValidationError(
                "Failed execution must contain an error or failed step."
            )

        for step in execution.steps:
            self.validate_step(step)

    def validate_step(self, step: WorkflowStep) -> None:
        """Validate an individual workflow step."""

        if not isinstance(step, WorkflowStep):
            raise WorkflowValidationError(
                "Expected a WorkflowStep instance."
            )

        if not step.name.strip():
            raise WorkflowValidationError(
                "Step name cannot be empty."
            )

        if step.execution_time_ms < 0:
            raise WorkflowValidationError(
                "Step execution time cannot be negative."
            )

        if (
            step.status == WorkflowStepStatus.FAILED
            and not step.error
        ):
            raise WorkflowValidationError(
                "Failed step must contain an error message."
            )

    def validate_input(
        self,
        input_data: dict[str, Any],
        *,
        required_fields: tuple[str, ...] = (),
        allowed_fields: tuple[str, ...] | None = None,
    ) -> None:
        """Validate workflow input fields."""

        if not isinstance(input_data, dict):
            raise WorkflowValidationError(
                "Workflow input must be a dictionary."
            )

        if not isinstance(required_fields, tuple):
            raise WorkflowValidationError(
                "required_fields must be a tuple."
            )

        if allowed_fields is not None and not isinstance(
            allowed_fields,
            tuple,
        ):
            raise WorkflowValidationError(
                "allowed_fields must be a tuple or None."
            )

        for field in required_fields:
            if not isinstance(field, str) or not field.strip():
                raise WorkflowValidationError(
                    "Required field names must be non-empty strings."
                )

            if field not in input_data:
                raise WorkflowValidationError(
                    f"Required input field '{field}' is missing."
                )

            if input_data[field] is None:
                raise WorkflowValidationError(
                    f"Required input field '{field}' cannot be None."
                )

        if allowed_fields is not None:
            unknown_fields = set(input_data) - set(allowed_fields)

            if unknown_fields:
                raise WorkflowValidationError(
                    "Unsupported input fields: "
                    + ", ".join(sorted(unknown_fields))
                )

    def validate_step_sequence(
        self,
        step_names: list[str],
        registered_steps: Mapping[str, Any],
    ) -> None:
        """Validate an ordered sequence of registered steps."""

        if not isinstance(step_names, list) or not step_names:
            raise WorkflowValidationError(
                "At least one workflow step is required."
            )

        if not isinstance(registered_steps, Mapping):
            raise WorkflowValidationError(
                "Registered steps must be a mapping."
            )

        for name in step_names:
            if not isinstance(name, str) or not name.strip():
                raise WorkflowValidationError(
                    "Every step name must be a non-empty string."
                )

            if name.strip() not in registered_steps:
                raise WorkflowValidationError(
                    f"Unregistered workflow step: {name}"
                )


def validate_workflow_definition(
    definition: WorkflowDefinition,
) -> None:
    """Convenience function for definition validation."""
    WorkflowValidator().validate_definition(definition)


def validate_workflow_execution(
    execution: WorkflowExecution,
) -> None:
    """Convenience function for execution validation."""
    WorkflowValidator().validate_execution(execution)


def validate_workflow_input(
    input_data: dict[str, Any],
    *,
    required_fields: tuple[str, ...] = (),
    allowed_fields: tuple[str, ...] | None = None,
) -> None:
    """Convenience function for workflow input validation."""
    WorkflowValidator().validate_input(
        input_data,
        required_fields=required_fields,
        allowed_fields=allowed_fields,
    )
