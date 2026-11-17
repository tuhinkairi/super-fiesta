
from context_aware_suggestion_rag.exceptions import WorkflowError
from context_aware_suggestion_rag.workflows.models import WorkflowDefinition
from context_aware_suggestion_rag.workflows.registry import WorkflowRegistry


registry = WorkflowRegistry()

definition = WorkflowDefinition(
    name="content_pipeline",
    description="Content recommendation and generation workflow",
    steps=["ingestion", "context_extraction", "generation"],
)

registry.register(definition)

assert registry.exists("content_pipeline")
assert len(registry) == 1

print("Workflow definition registration: PASS")


retrieved = registry.get("content_pipeline")

assert retrieved.name == "content_pipeline"
assert len(retrieved.steps) == 3

print("Workflow definition retrieval: PASS")


try:
    registry.register(definition)
except WorkflowError:
    print("Duplicate definition prevention: PASS")
else:
    raise AssertionError("Duplicate definition was accepted.")


disabled = WorkflowDefinition(
    name="disabled_pipeline",
    steps=["ingestion"],
    enabled=False,
)

registry.register(disabled)

enabled = registry.list_definitions(enabled_only=True)

assert len(enabled) == 1
assert enabled[0].name == "content_pipeline"

print("Enabled workflow filtering: PASS")


replacement = WorkflowDefinition(
    name="content_pipeline",
    description="Updated pipeline",
    steps=["ingestion", "generation"],
)

registry.register(replacement, replace=True)

assert registry.get("content_pipeline").description == "Updated pipeline"

print("Workflow definition replacement: PASS")


assert registry.unregister("disabled_pipeline") is True
assert registry.unregister("disabled_pipeline") is False

print("Workflow definition removal: PASS")


registry.clear()

assert len(registry) == 0

print("Workflow registry clearing: PASS")

print("\nAll workflow registry tests passed.")
