
from context_aware_suggestion_rag.workflows.engine import WorkflowEngine
from context_aware_suggestion_rag.workflows.executor import WorkflowExecutor
from context_aware_suggestion_rag.workflows.history import WorkflowHistory
from context_aware_suggestion_rag.workflows.models import WorkflowDefinition
from context_aware_suggestion_rag.workflows.service import (
    WorkflowService,
    create_workflow_service,
)


def add_step(data):
    return {"result": data.get("value", 0) + 10}


def multiply_step(data):
    return {"final_result": data["result"] * 2}


def main():
    engine = WorkflowEngine()
    engine.register_step("add", add_step)
    engine.register_step("multiply", multiply_step)

    executor = WorkflowExecutor(engine=engine)

    history = WorkflowHistory()
    service = WorkflowService(
        executor=executor,
        history=history,
    )

    definition = WorkflowDefinition(
        name="sample_workflow",
        description="Service test workflow",
        steps=["add", "multiply"],
    )

    # Single execution
    result = service.execute(
        definition=definition,
        input_data={"value": 5},
    )

    assert result.output_data["final_result"] == 30
    assert len(service.get_history()) == 1
    print("Single workflow execution: PASS")

    # Retrieve execution
    retrieved = service.get_execution(result.execution_id)

    assert retrieved is not None
    assert retrieved.execution_id == result.execution_id
    print("Execution retrieval: PASS")

    # Latest execution
    latest = service.get_latest_execution("sample_workflow")

    assert latest is not None
    assert latest.execution_id == result.execution_id
    print("Latest execution retrieval: PASS")

    # Multiple executions
    results = service.execute_many(
        definitions=[definition, definition],
        input_data={"value": 2},
    )

    assert len(results) == 2
    assert len(service.get_history()) == 3
    print("Multiple workflow executions: PASS")

    # History limit
    limited_history = service.get_history(limit=2)

    assert len(limited_history) == 2
    print("Execution history limit: PASS")

    # Remove execution
    removed = service.remove_execution(result.execution_id)

    assert removed is True
    assert service.get_execution(result.execution_id) is None
    print("Execution removal: PASS")

    # Clear history
    service.clear_history()

    assert len(service.get_history()) == 0
    print("Execution history clearing: PASS")

    # Factory
    factory_service = create_workflow_service(executor=executor)

    assert isinstance(factory_service, WorkflowService)
    print("Workflow service factory: PASS")

    print("\nAll workflow service tests passed.")


if __name__ == "__main__":
    main()
