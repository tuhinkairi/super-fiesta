
from context_aware_suggestion_rag.workflows.engine import WorkflowEngine
from context_aware_suggestion_rag.workflows.models import (
    WorkflowExecutionStatus,
    WorkflowStepStatus,
)


def ingest(data):
    return {"document": "Sample document"}


def extract_context(data):
    return {"context": "Artificial Intelligence"}


def generate(data):
    return {"suggestion": "Create an AI tutorial"}


engine = WorkflowEngine({
    "ingestion": ingest,
    "context_extraction": extract_context,
    "generation": generate,
})

print("Workflow engine initialization: PASS")

result = engine.execute(
    workflow_name="content_pipeline",
    step_names=[
        "ingestion",
        "context_extraction",
        "generation",
    ],
    input_data={"source": "sample.pdf"},
)

assert result.status == WorkflowExecutionStatus.COMPLETED
assert result.total_steps == 3
assert result.completed_steps == 3
assert result.output_data["suggestion"] == "Create an AI tutorial"

print("Sequential workflow execution: PASS")


def failing_step(data):
    raise RuntimeError("Simulated processing failure")


engine.register_step("failure", failing_step)

failed_result = engine.execute(
    workflow_name="failure_pipeline",
    step_names=["ingestion", "failure", "generation"],
    input_data={},
)

assert failed_result.status == WorkflowExecutionStatus.FAILED
assert failed_result.failed_steps == 1
assert len(failed_result.steps) == 2
assert failed_result.steps[1].status == WorkflowStepStatus.FAILED
assert "Simulated processing failure" in failed_result.error

print("Workflow failure handling: PASS")


assert engine.unregister_step("failure") is True
assert engine.unregister_step("failure") is False

print("Step registration and removal: PASS")

print("\nAll workflow engine tests passed.")
