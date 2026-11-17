
from context_aware_suggestion_rag.workflows.models import (
    WorkflowDefinition,
    WorkflowExecution,
    WorkflowExecutionStatus,
    WorkflowStep,
    WorkflowStepStatus,
)
from context_aware_suggestion_rag.workflows.validators import (
    WorkflowValidationError,
    WorkflowValidator,
    validate_workflow_definition,
    validate_workflow_execution,
    validate_workflow_input,
)


validator = WorkflowValidator()

definition = WorkflowDefinition(
    name="content_pipeline",
    steps=["ingestion", "context_extraction", "generation"],
)

validator.validate_definition(definition)
validate_workflow_definition(definition)

print("Workflow definition validation: PASS")


execution = WorkflowExecution(
    workflow_name="content_pipeline",
    status=WorkflowExecutionStatus.COMPLETED,
    steps=[
        WorkflowStep(
            name="ingestion",
            status=WorkflowStepStatus.COMPLETED,
        ),
        WorkflowStep(
            name="generation",
            status=WorkflowStepStatus.COMPLETED,
        ),
    ],
)

validator.validate_execution(execution)
validate_workflow_execution(execution)

print("Workflow execution validation: PASS")


validator.validate_input(
    {"document": "sample.pdf", "language": "en"},
    required_fields=("document",),
    allowed_fields=("document", "language"),
)

validate_workflow_input(
    {"document": "sample.pdf"},
    required_fields=("document",),
)

print("Workflow input validation: PASS")


try:
    validator.validate_input(
        {},
        required_fields=("document",),
    )
except WorkflowValidationError:
    print("Missing required input detection: PASS")
else:
    raise AssertionError("Missing required input was accepted.")


try:
    validator.validate_input(
        {"document": "sample.pdf", "unknown": "value"},
        allowed_fields=("document",),
    )
except WorkflowValidationError:
    print("Unknown input field detection: PASS")
else:
    raise AssertionError("Unknown input field was accepted.")


try:
    validator.validate_step_sequence(
        ["ingestion", "unknown"],
        {"ingestion": object()},
    )
except WorkflowValidationError:
    print("Unregistered step detection: PASS")
else:
    raise AssertionError("Unregistered workflow step was accepted.")


print("\nAll workflow validator tests passed.")
