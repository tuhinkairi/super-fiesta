
from context_aware_suggestion_rag.workflows.executor import (
    WorkflowExecutor,
    create_workflow_executor,
)
from context_aware_suggestion_rag.workflows.models import (
    WorkflowDefinition,
    WorkflowExecutionStatus,
)


def ingest(data):
    return {"document_text": "Artificial Intelligence document"}


def extract(data):
    return {"topic": "Artificial Intelligence"}


def generate(data):
    return {"suggestion": "Create an AI tutorial"}


executor = create_workflow_executor(
    steps={
        "ingestion": ingest,
        "context_extraction": extract,
        "generation": generate,
    }
)

print("Workflow executor initialization: PASS")


definition = WorkflowDefinition(
    name="content_pipeline",
    steps=[
        "ingestion",
        "context_extraction",
        "generation",
    ],
)

result = executor.execute(
    definition,
    {"document": "sample.pdf"},
)

assert result.status == WorkflowExecutionStatus.COMPLETED
assert result.total_steps == 3
assert result.output_data["suggestion"] == "Create an AI tutorial"

print("Definition-based workflow execution: PASS")


results = executor.execute_many(
    [definition, definition],
    {"document": "sample.pdf"},
)

assert len(results) == 2
assert all(
    item.status == WorkflowExecutionStatus.COMPLETED
    for item in results
)

print("Multiple workflow execution: PASS")


try:
    executor.execute(
        WorkflowDefinition(
            name="invalid_pipeline",
            steps=["missing_step"],
        ),
        {},
    )
except ValueError:
    print("Unregistered workflow step validation: PASS")
else:
    raise AssertionError("Unregistered step was accepted.")


print("\nAll workflow executor tests passed.")
