"""
Workflow execution history.

Provides thread-safe storage and retrieval of workflow
execution records.
"""

from __future__ import annotations

from threading import RLock

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.workflows.models import (
    WorkflowExecution,
    WorkflowExecutionStatus,
)


class WorkflowHistory:
    """Stores workflow execution records."""

    def __init__(self, max_records: int | None = None) -> None:
        if max_records is not None:
            if (
                isinstance(max_records, bool)
                or not isinstance(max_records, int)
                or max_records <= 0
            ):
                raise ValueError(
                    "max_records must be a positive integer or None."
                )

        self.max_records = max_records
        self._records: list[WorkflowExecution] = []
        self._lock = RLock()

    def add(self, execution: WorkflowExecution) -> None:
        """Add an execution record."""

        if not isinstance(execution, WorkflowExecution):
            raise TypeError(
                "Expected a WorkflowExecution instance."
            )

        with self._lock:
            self._records.append(execution)

            if self.max_records is not None:
                overflow = len(self._records) - self.max_records

                if overflow > 0:
                    del self._records[:overflow]

    def get(self, execution_id: str) -> WorkflowExecution | None:
        """Retrieve an execution by its ID."""

        if not isinstance(execution_id, str) or not execution_id.strip():
            raise ValueError("Execution ID cannot be empty.")

        with self._lock:
            for execution in reversed(self._records):
                if execution.execution_id == execution_id:
                    return execution

        return None

    def list_all(self) -> tuple[WorkflowExecution, ...]:
        """Return all execution records in insertion order."""

        with self._lock:
            return tuple(self._records)

    def filter_by_workflow(
        self,
        workflow_name: str,
    ) -> tuple[WorkflowExecution, ...]:
        """Return executions belonging to a workflow."""

        if not isinstance(workflow_name, str) or not workflow_name.strip():
            raise ValueError("Workflow name cannot be empty.")

        normalized_name = workflow_name.strip()

        with self._lock:
            return tuple(
                record
                for record in self._records
                if record.workflow_name == normalized_name
            )

    def filter_by_status(
        self,
        status: WorkflowExecutionStatus,
    ) -> tuple[WorkflowExecution, ...]:
        """Return executions matching a status."""

        if not isinstance(status, WorkflowExecutionStatus):
            status = WorkflowExecutionStatus(status)

        with self._lock:
            return tuple(
                record
                for record in self._records
                if record.status == status
            )

    def latest(
        self,
        limit: int = 10,
    ) -> tuple[WorkflowExecution, ...]:
        """Return the most recent inserted execution records."""

        if (
            isinstance(limit, bool)
            or not isinstance(limit, int)
            or limit <= 0
        ):
            raise ValueError("Limit must be a positive integer.")

        with self._lock:
            return tuple(reversed(self._records[-limit:]))

    def remove(self, execution_id: str) -> bool:
        """Remove an execution record by ID."""

        if not isinstance(execution_id, str) or not execution_id.strip():
            raise ValueError("Execution ID cannot be empty.")

        with self._lock:
            for index, execution in enumerate(self._records):
                if execution.execution_id == execution_id:
                    del self._records[index]
                    return True

        return False

    def clear(self) -> None:
        """Remove all execution records."""

        with self._lock:
            self._records.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._records)
