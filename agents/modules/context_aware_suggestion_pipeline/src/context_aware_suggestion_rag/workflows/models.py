"""
Workflow models.

Defines workflow execution status, step information,
execution results, and workflow history.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


def current_utc_time() -> datetime:
    """Return the current UTC timestamp."""
    return datetime.now(timezone.utc)


class WorkflowExecutionStatus(str, Enum):
    """Possible states of a workflow execution."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowStepStatus(str, Enum):
    """Possible states of an individual workflow step."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass(slots=True)
class WorkflowStep:
    """Represents one step in a workflow."""

    name: str
    description: str = ""
    status: WorkflowStepStatus = WorkflowStepStatus.PENDING
    input_data: dict[str, Any] = field(default_factory=dict)
    output_data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    execution_time_ms: float = 0.0

    def __post_init__(self) -> None:
        self.name = self.name.strip() if isinstance(self.name, str) else ""

        if not self.name:
            raise ValueError("Workflow step name cannot be empty.")

        if not isinstance(self.description, str):
            raise TypeError("Step description must be a string.")

        if not isinstance(self.status, WorkflowStepStatus):
            self.status = WorkflowStepStatus(self.status)

        if not isinstance(self.input_data, dict):
            raise TypeError("Step input_data must be a dictionary.")

        if not isinstance(self.output_data, dict):
            raise TypeError("Step output_data must be a dictionary.")

        if self.error is not None and not isinstance(self.error, str):
            raise TypeError("Step error must be a string or None.")

        if (
            isinstance(self.execution_time_ms, bool)
            or not isinstance(self.execution_time_ms, (int, float))
            or self.execution_time_ms < 0
        ):
            raise ValueError("Execution time must be a non-negative number.")


@dataclass(slots=True)
class WorkflowExecution:
    """Represents one complete workflow execution."""

    workflow_name: str
    execution_id: str = field(
        default_factory=lambda: f"wf_{uuid4().hex}"
    )
    status: WorkflowExecutionStatus = WorkflowExecutionStatus.PENDING
    steps: list[WorkflowStep] = field(default_factory=list)
    input_data: dict[str, Any] = field(default_factory=dict)
    output_data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    created_at: datetime = field(default_factory=current_utc_time)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    execution_time_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.workflow_name = (
            self.workflow_name.strip()
            if isinstance(self.workflow_name, str)
            else ""
        )

        if not self.workflow_name:
            raise ValueError("Workflow name cannot be empty.")

        if not isinstance(self.execution_id, str) or not self.execution_id.strip():
            raise ValueError("Execution ID cannot be empty.")

        if not isinstance(self.status, WorkflowExecutionStatus):
            self.status = WorkflowExecutionStatus(self.status)

        if not isinstance(self.steps, list):
            raise TypeError("Workflow steps must be a list.")

        if not all(isinstance(step, WorkflowStep) for step in self.steps):
            raise TypeError("Every workflow step must be a WorkflowStep.")

        for field_name, value in (
            ("input_data", self.input_data),
            ("output_data", self.output_data),
            ("metadata", self.metadata),
        ):
            if not isinstance(value, dict):
                raise TypeError(f"{field_name} must be a dictionary.")

        if self.error is not None and not isinstance(self.error, str):
            raise TypeError("Workflow error must be a string or None.")

        if (
            isinstance(self.execution_time_ms, bool)
            or not isinstance(self.execution_time_ms, (int, float))
            or self.execution_time_ms < 0
        ):
            raise ValueError("Execution time must be a non-negative number.")

    @property
    def total_steps(self) -> int:
        """Return the number of workflow steps."""
        return len(self.steps)

    @property
    def completed_steps(self) -> int:
        """Return the number of completed steps."""
        return sum(
            step.status == WorkflowStepStatus.COMPLETED
            for step in self.steps
        )

    @property
    def failed_steps(self) -> int:
        """Return the number of failed steps."""
        return sum(
            step.status == WorkflowStepStatus.FAILED
            for step in self.steps
        )

    @property
    def success_rate(self) -> float:
        """Return the percentage of successfully completed steps."""
        if not self.steps:
            return 0.0

        return self.completed_steps / self.total_steps


@dataclass(slots=True)
class WorkflowDefinition:
    """Describes a workflow and its ordered steps."""

    name: str
    description: str = ""
    steps: list[str] = field(default_factory=list)
    enabled: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.name = self.name.strip() if isinstance(self.name, str) else ""

        if not self.name:
            raise ValueError("Workflow definition name cannot be empty.")

        if not isinstance(self.steps, list):
            raise TypeError("Workflow definition steps must be a list.")

        normalized_steps: list[str] = []

        for step in self.steps:
            if not isinstance(step, str) or not step.strip():
                raise ValueError("Every workflow step name must be non-empty.")

            normalized_steps.append(step.strip())

        if len(normalized_steps) != len(set(normalized_steps)):
            raise ValueError("Workflow step names must be unique.")

        self.steps = normalized_steps

        if not isinstance(self.enabled, bool):
            raise TypeError("Workflow enabled must be a boolean.")

        if not isinstance(self.metadata, dict):
            raise TypeError("Workflow metadata must be a dictionary.")
