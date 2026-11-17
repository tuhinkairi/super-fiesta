
from context_aware_suggestion_rag.workflows.state import WorkflowState


state = WorkflowState({
    "document": "sample.pdf",
    "status": "pending",
})

assert state.get("document") == "sample.pdf"
assert state.get("missing", "default") == "default"

print("Workflow state initialization: PASS")


state.set("status", "processing")
assert state.get("status") == "processing"

state.update({
    "context": "Artificial Intelligence",
    "keywords": ["AI", "RAG"],
})

assert state.get("context") == "Artificial Intelligence"
assert state.get("keywords") == ["AI", "RAG"]

print("Workflow state updates: PASS")


state.add_error("Context extraction failed")

assert len(state.get_errors()) == 1
assert state.get_errors()[0] == "Context extraction failed"

state.clear_errors()
assert state.get_errors() == ()

print("Workflow error tracking: PASS")


snapshot = state.snapshot()
snapshot["status"] = "modified"

assert state.get("status") == "processing"

print("Workflow state snapshot isolation: PASS")


assert state.delete("context") is True
assert state.delete("context") is False
assert "context" not in state

print("Workflow state deletion: PASS")


assert state.version > 0

state.clear()

assert len(state) == 0
assert state.get_errors() == ()

print("Workflow state clearing: PASS")

print("\nAll workflow state tests passed.")
