
from context_aware_suggestion_rag.interfaces.workflow_provider import (
    WorkflowProvider,
)
from context_aware_suggestion_rag.workflows.models import (
    WorkflowDefinition,
    WorkflowExecution,
    WorkflowExecutionStatus,
)


class FakeWorkflowProvider(WorkflowProvider):

    def execute(self, definition, input_data, metadata=None):
        return WorkflowExecution(
            workflow_name=definition.name,
            status=WorkflowExecutionStatus.COMPLETED,
            input_data=dict(input_data),
            output_data={"result": "success"},
            metadata=dict(metadata or {}),
        )

    def health_check(self):
        return True


def main():
    provider = FakeWorkflowProvider()

    assert isinstance(provider, WorkflowProvider)
    print("Workflow provider inheritance: PASS")

    assert provider.health_check()
    print("Workflow provider health check: PASS")

    definition = WorkflowDefinition(
        name="test_workflow",
        description="Interface test workflow",
        steps=["step_one"],
    )

    execution = provider.execute(
        definition=definition,
        input_data={"value": 10},
        metadata={"source": "test"},
    )

    assert isinstance(execution, WorkflowExecution)
    assert execution.workflow_name == "test_workflow"
    assert execution.status == WorkflowExecutionStatus.COMPLETED
    print("Workflow execution interface: PASS")

    assert execution.output_data["result"] == "success"
    assert execution.metadata["source"] == "test"
    print("Workflow execution result: PASS")

    provider.close()
    print("Workflow provider close interface: PASS")

    print("\nAll workflow provider interface tests passed.")


if __name__ == "__main__":
    main()
