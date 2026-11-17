
from context_aware_suggestion_rag.workflows.base import (
    BasePipelineWorkflow,
    BaseWorkflowManager,
)


assert BasePipelineWorkflow.__abstractmethods__ == {
    "execute",
    "validate_input",
    "get_definition",
}

print("Pipeline workflow abstract methods: PASS")


assert BaseWorkflowManager.__abstractmethods__ == {
    "register",
    "unregister",
    "get",
    "list_workflows",
    "execute",
}

print("Workflow manager abstract methods: PASS")


print("\nAll workflow base tests passed.")
