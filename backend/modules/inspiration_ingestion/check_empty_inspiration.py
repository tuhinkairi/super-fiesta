from unittest.mock import Mock

from modules.story_intelligence.story_rag import StoryRAG
from modules.story_intelligence.models.suggestion import SuggestionGraph


def main():
    print("Testing empty inspiration library...\n")

    mock_llm = Mock()
    mock_inspiration_service = Mock()

    # Simulate an empty inspiration library.
    mock_inspiration_service.metadata_store.count.return_value = 0

    story_rag = StoryRAG(
        llm_client=mock_llm,
        inspiration_service=mock_inspiration_service,
    )

    # Mock the suggestion workflow.
    mock_workflow = Mock()

    expected_result = SuggestionGraph(
        project_id="empty-inspiration-test",
        suggestions=[],
    )

    mock_workflow.generate_suggestions.return_value = expected_result
    story_rag._suggestion_workflow = mock_workflow

    # Generate suggestions without any inspiration material.
    result = story_rag.generate_suggestions(
        story_context="A detective investigates a mysterious disappearance.",
        max_suggestions=3,
    )

    # Verify that semantic search was skipped.
    mock_inspiration_service.search.assert_not_called()
    print("PASS: Empty library did not trigger inspiration search.")

    # Verify that the workflow received an empty inspiration list.
    arguments = mock_workflow.generate_suggestions.call_args.kwargs

    assert arguments["inspiration_results"] == []
    print("PASS: Suggestion workflow received an empty inspiration list.")

    # Verify that suggestions were still returned.
    assert result == expected_result
    print("PASS: Suggestions generated without inspiration.")

    story_rag.close()

    print("\nAll empty inspiration checks passed!")


if __name__ == "__main__":
    main()
