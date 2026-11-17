"""
Workflow execution engine.

Executes workflow steps and records execution status,
timing, outputs, and failures.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from time import perf_counter
from typing import Any

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.workflows.models import (
    WorkflowExecution,
    WorkflowExecutionStatus,
    WorkflowStep,
    WorkflowStepStatus,
)


WorkflowStepCallable = Callable[
    [dict[str, Any]],
    Mapping[str, Any] | None,
]


class WorkflowEngine:
    """Executes a sequence of named workflow operations."""

    def __init__(
        self,
        steps: Mapping[str, WorkflowStepCallable] | None = None,
    ) -> None:
        self._steps: dict[str, WorkflowStepCallable] = {}

        if steps is not None:
            for name, operation in steps.items():
                self.register_step(name, operation)

    def register_step(
        self,
        name: str,
        operation: WorkflowStepCallable,
    ) -> None:
        """Register a named step operation."""
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Step name cannot be empty.")

        if not callable(operation):
            raise TypeError("Step operation must be callable.")

        normalized_name = name.strip()

        if normalized_name in self._steps:
            raise ValueError(
                f"Workflow step '{normalized_name}' is already registered."
            )

        self._steps[normalized_name] = operation

    def unregister_step(self, name: str) -> bool:
        """Unregister a step operation."""
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Step name cannot be empty.")

        return self._steps.pop(name.strip(), None) is not None

    def get_registered_steps(self) -> tuple[str, ...]:
        """Return registered step names."""
        return tuple(self._steps)

    def execute(
        self,
        workflow_name: str,
        step_names: list[str],
        input_data: dict[str, Any],
        *,
        metadata: dict[str, Any] | None = None,
    ) -> WorkflowExecution:
        """Execute the requested steps in order."""

        if not isinstance(workflow_name, str) or not workflow_name.strip():
            raise ValueError("Workflow name cannot be empty.")

        if not isinstance(step_names, list) or not step_names:
            raise ValueError("At least one workflow step is required.")

        if not isinstance(input_data, dict):
            raise TypeError("Workflow input must be a dictionary.")

        if metadata is not None and not isinstance(metadata, dict):
            raise TypeError("Workflow metadata must be a dictionary.")

        for name in step_names:
            if not isinstance(name, str) or not name.strip():
                raise ValueError("Every step name must be non-empty.")

            if name.strip() not in self._steps:
                raise ValueError(f"Unregistered workflow step: {name}")

        execution = WorkflowExecution(
            workflow_name=workflow_name.strip(),
            input_data=dict(input_data),
            metadata=dict(metadata or {}),
        )

        execution.status = WorkflowExecutionStatus.RUNNING
        execution.started_at = execution.created_at

        workflow_data = dict(input_data)
        total_start = perf_counter()

        for name in step_names:
            normalized_name = name.strip()

            step = WorkflowStep(
                name=normalized_name,
                input_data=dict(workflow_data),
                status=WorkflowStepStatus.RUNNING,
                started_at=execution.started_at,
            )

            execution.steps.append(step)
            step_start = perf_counter()

            try:
                result = self._steps[normalized_name](dict(workflow_data))

                if result is not None and not isinstance(result, Mapping):
                    raise TypeError(
                        f"Step '{normalized_name}' must return a mapping or None."
                    )

                if result is not None:
                    workflow_data.update(dict(result))

                step.output_data = dict(result or {})
                step.status = WorkflowStepStatus.COMPLETED

            except Exception as exc:
                step.status = WorkflowStepStatus.FAILED
                step.error = str(exc)

                step.execution_time_ms = (
                    perf_counter() - step_start
                ) * 1000

                step.completed_at = _safe_current_time()

                execution.status = WorkflowExecutionStatus.FAILED
                execution.error = (
                    f"Step '{normalized_name}' failed: {exc}"
                )
                break

            finally:
                if step.completed_at is None:
                    step.completed_at = _safe_current_time()

                if step.execution_time_ms == 0.0:
                    step.execution_time_ms = (
                        perf_counter() - step_start
                    ) * 1000

        execution.output_data = workflow_data
        execution.execution_time_ms = (
            perf_counter() - total_start
        ) * 1000

        execution.completed_at = _safe_current_time()

        if execution.status != WorkflowExecutionStatus.FAILED:
            execution.status = WorkflowExecutionStatus.COMPLETED

        return execution


def _safe_current_time():
    """Return a UTC timestamp for workflow lifecycle records."""
    from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.workflows.models import current_utc_time

    return current_utc_time()
