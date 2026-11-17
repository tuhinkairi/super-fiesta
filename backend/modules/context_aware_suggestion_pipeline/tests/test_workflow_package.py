
from context_aware_suggestion_rag.workflows import (
    BasePipelineWorkflow,
    BaseWorkflowManager,
    WorkflowDefinition,
    WorkflowEngine,
    WorkflowExecution,
    WorkflowExecutionStatus,
    WorkflowExecutor,
    WorkflowHistory,
    WorkflowManager,
    WorkflowRegistry,
    WorkflowService,
    WorkflowState,
    WorkflowStep,
    WorkflowStepStatus,
    WorkflowValidationError,
    WorkflowValidator,
    create_workflow_executor,
    create_workflow_service,
)


def main():
    exported_classes = [
        BasePipelineWorkflow,
        BaseWorkflowManager,
        WorkflowDefinition,
        WorkflowEngine,
        WorkflowExecution,
        WorkflowExecutionStatus,
        WorkflowExecutor,
        WorkflowHistory,
        WorkflowManager,
        WorkflowRegistry,
        WorkflowService,
        WorkflowState,
        WorkflowStep,
        WorkflowStepStatus,
        WorkflowValidationError,
        WorkflowValidator,
    ]

    for exported_class in exported_classes:
        assert exported_class is not None

    print("Workflow package imports: PASS")

    assert callable(create_workflow_executor)
    assert callable(create_workflow_service)

    print("Workflow factory exports: PASS")

    print("\nAll workflow package export tests passed.")


if __name__ == "__main__":
    main()
