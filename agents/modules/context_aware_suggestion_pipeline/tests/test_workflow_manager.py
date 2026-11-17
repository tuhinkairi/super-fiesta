
from context_aware_suggestion_rag.exceptions import WorkflowError
from context_aware_suggestion_rag.workflows.base import BasePipelineWorkflow
from context_aware_suggestion_rag.workflows.manager import WorkflowManager
from context_aware_suggestion_rag.workflows.models import (
    WorkflowDefinition,
    WorkflowExecution,
    WorkflowExecutionStatus,
)


class FakeWorkflow(BasePipelineWorkflow):

    def get_definition(self):
        return WorkflowDefinition(
            name="test_pipeline",
            steps=["ingestion", "generation"],
        )

    def validate_input(self, input_data):
        if "document" not in input_data:
            raise ValueError("Document is required.")

    def execute(self, input_data, *, metadata=None):
        return WorkflowExecution(
            workflow_name="test_pipeline",
            input_data=input_data,
            output_data={"result": "success"},
            status=WorkflowExecutionStatus.COMPLETED,
            metadata=metadata or {},
        )


manager = WorkflowManager()
workflow = FakeWorkflow()

manager.register(workflow)

assert manager.list_workflows() == ("test_pipeline",)
print("Workflow registration: PASS")


assert manager.get("test_pipeline") is workflow
print("Workflow retrieval: PASS")


try:
    manager.register(workflow)
except WorkflowError:
    print("Duplicate registration prevention: PASS")
else:
    raise AssertionError("Duplicate workflow registration was accepted.")


result = manager.execute(
    "test_pipeline",
    {"document": "sample.pdf"},
    metadata={"source": "test"},
)

assert result.status == WorkflowExecutionStatus.COMPLETED
assert result.output_data["result"] == "success"
print("Workflow execution delegation: PASS")


failed_result = manager.execute(
    "test_pipeline",
    {},
)

assert failed_result.status == WorkflowExecutionStatus.FAILED
assert "Document is required." in failed_result.error
print("Workflow input validation: PASS")


assert manager.unregister("test_pipeline") is True
assert manager.unregister("test_pipeline") is False
print("Workflow unregistration: PASS")


try:
    manager.get("test_pipeline")
except WorkflowError:
    print("Unknown workflow handling: PASS")
else:
    raise AssertionError("Unknown workflow was retrieved.")


print("\nAll workflow manager tests passed.")
