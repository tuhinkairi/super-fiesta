"""
High-level workflow service.

Coordinates workflow execution and execution-history management.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.workflows.executor import (
    WorkflowExecutor,
)
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.workflows.history import (
    WorkflowHistory,
)
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.workflows.models import (
    WorkflowDefinition,
    WorkflowExecution,
)


class WorkflowService:
    """Provides a unified interface for workflow execution and history."""

    def __init__(
        self,
        executor: WorkflowExecutor,
        history: WorkflowHistory | None = None,
    ) -> None:
        if not isinstance(executor, WorkflowExecutor):
            raise TypeError("executor must be a WorkflowExecutor instance")

        if history is not None and not isinstance(history, WorkflowHistory):
            raise TypeError("history must be a WorkflowHistory instance")

        self.executor = executor
        self.history = history or WorkflowHistory()

    def execute(
        self,
        definition: WorkflowDefinition,
        input_data: Mapping[str, Any],
        metadata: Mapping[str, Any] | None = None,
    ) -> WorkflowExecution:
        """
        Execute a workflow and record its execution.

        Execution results are recorded regardless of whether the workflow
        completes successfully or returns a failed execution.
        """
        execution = self.executor.execute(
            definition=definition,
            input_data=input_data,
            metadata=metadata,
        )

        self.history.add(execution)
        return execution

    def execute_many(
        self,
        definitions: Sequence[WorkflowDefinition],
        input_data: Mapping[str, Any],
        metadata: Mapping[str, Any] | None = None,
    ) -> list[WorkflowExecution]:
        """Execute multiple workflow definitions sequentially."""
        if isinstance(definitions, (str, bytes)):
            raise TypeError("definitions must be a sequence of WorkflowDefinition")

        if not isinstance(definitions, Sequence):
            raise TypeError("definitions must be a sequence")

        results: list[WorkflowExecution] = []

        for definition in definitions:
            results.append(
                self.execute(
                    definition=definition,
                    input_data=input_data,
                    metadata=metadata,
                )
            )

        return results

    def get_execution(
        self,
        execution_id: str,
    ) -> WorkflowExecution | None:
        """Retrieve an execution by its unique ID."""
        return self.history.get(execution_id)

    def get_history(
        self,
        workflow_name: str | None = None,
        limit: int | None = None,
    ) -> list[WorkflowExecution]:
        """Retrieve execution history, optionally filtered by workflow."""
        if workflow_name is not None:
            executions = self.history.filter_by_workflow(workflow_name)
        else:
            executions = self.history.list_all()

        if limit is not None:
            if isinstance(limit, bool) or not isinstance(limit, int) or limit <= 0:
                raise ValueError("limit must be a positive integer")

            executions = executions[-limit:]

        return executions

    def get_latest_execution(
        self,
        workflow_name: str,
    ) -> WorkflowExecution | None:
        """Retrieve the latest execution of a particular workflow."""
        executions = self.history.filter_by_workflow(workflow_name)

        if not executions:
            return None

        return executions[-1]

    def clear_history(self) -> None:
        """Remove all stored execution-history records."""
        self.history.clear()

    def remove_execution(self, execution_id: str) -> bool:
        """Remove a specific execution from history."""
        return self.history.remove(execution_id)


def create_workflow_service(
    executor: WorkflowExecutor,
    history: WorkflowHistory | None = None,
) -> WorkflowService:
    """Create a configured workflow service."""
    return WorkflowService(
        executor=executor,
        history=history,
    )
