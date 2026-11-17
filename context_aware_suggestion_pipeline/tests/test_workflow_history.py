
from context_aware_suggestion_rag.workflows.history import WorkflowHistory
from context_aware_suggestion_rag.workflows.models import (
    WorkflowExecution,
    WorkflowExecutionStatus,
)


history = WorkflowHistory(max_records=3)

first = WorkflowExecution(
    workflow_name="content_pipeline",
    status=WorkflowExecutionStatus.COMPLETED,
)

second = WorkflowExecution(
    workflow_name="content_pipeline",
    status=WorkflowExecutionStatus.FAILED,
    error="Generation failed",
)

third = WorkflowExecution(
    workflow_name="news_pipeline",
    status=WorkflowExecutionStatus.COMPLETED,
)

history.add(first)
history.add(second)
history.add(third)

assert len(history) == 3

print("Workflow history storage: PASS")


assert history.get(first.execution_id) is first
assert history.get("unknown_id") is None

print("Execution retrieval: PASS")


content_records = history.filter_by_workflow("content_pipeline")

assert len(content_records) == 2

failed_records = history.filter_by_status(
    WorkflowExecutionStatus.FAILED
)

assert len(failed_records) == 1

print("Workflow and status filtering: PASS")


latest_records = history.latest(2)

assert latest_records[0] is third
assert latest_records[1] is second

print("Latest execution retrieval: PASS")


fourth = WorkflowExecution(
    workflow_name="generation_pipeline",
)

history.add(fourth)

assert len(history) == 3
assert history.get(first.execution_id) is None
assert history.get(fourth.execution_id) is fourth

print("History size limit: PASS")


assert history.remove(second.execution_id) is True
assert history.remove(second.execution_id) is False

print("Execution removal: PASS")


history.clear()

assert len(history) == 0

print("History clearing: PASS")

print("\nAll workflow history tests passed.")
