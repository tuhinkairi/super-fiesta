
from context_aware_suggestion_rag.workflows.models import (
    WorkflowDefinition,
    WorkflowExecution,
    WorkflowExecutionStatus,
    WorkflowStep,
    WorkflowStepStatus,
)


step = WorkflowStep(
    name="document_ingestion",
    status=WorkflowStepStatus.COMPLETED,
    execution_time_ms=120.5,
)

assert step.name == "document_ingestion"
assert step.status == WorkflowStepStatus.COMPLETED

print("Workflow step creation: PASS")


execution = WorkflowExecution(
    workflow_name="content_suggestion",
    steps=[
        step,
        WorkflowStep(
            name="context_extraction",
            status=WorkflowStepStatus.COMPLETED,
        ),
        WorkflowStep(
            name="recommendation",
            status=WorkflowStepStatus.FAILED,
        ),
    ],
)

assert execution.total_steps == 3
assert execution.completed_steps == 2
assert execution.failed_steps == 1
assert abs(execution.success_rate - (2 / 3)) < 0.0001

print("Workflow execution metrics: PASS")


definition = WorkflowDefinition(
    name="content_pipeline",
    steps=[
        "ingestion",
        "context_extraction",
        "recommendation",
        "generation",
    ],
)

assert len(definition.steps) == 4
assert definition.enabled is True

print("Workflow definition: PASS")


assert execution.status == WorkflowExecutionStatus.PENDING

print("Workflow status defaults: PASS")
print("\nAll workflow model tests passed.")
