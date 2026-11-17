from unittest.mock import Mock

from modules.story_intelligence.story_rag import StoryRAG
from modules.story_intelligence.models.suggestion import SuggestionGraph
from modules.inspiration_ingestion.types import InspirationRecord


def main():

    print("Testing Story Intelligence + Inspiration integration...\n")

    # --------------------------------------------------
    # 1. CREATE MOCK LLM CLIENT
    # --------------------------------------------------

    mock_llm = Mock()

    # --------------------------------------------------
    # 2. CREATE MOCK INSPIRATION SERVICE
    # --------------------------------------------------

    mock_inspiration_service = Mock()

    inspiration_record = InspirationRecord(
        file_name="mysterious_forest.txt",
        content_type="text",
        extracted_text=(
            "An ancient forest contains forgotten pathways " "and mysterious symbols."
        ),
        summary="A mysterious ancient forest.",
        description=("A forest with hidden pathways and forgotten symbols."),
        keywords=["forest", "mystery", "symbols"],
        themes=["mystery", "discovery"],
        mood_tags=["dark", "mysterious"],
    )

    mock_inspiration_service.metadata_store.count.return_value = 1

    mock_inspiration_service.search.return_value = [
        {
            "record": inspiration_record,
            "similarity": 0.91,
        }
    ]

    # --------------------------------------------------
    # 3. INITIALIZE STORYRAG
    # --------------------------------------------------

    story_rag = StoryRAG(
        llm_client=mock_llm,
        inspiration_service=mock_inspiration_service,
    )

    # --------------------------------------------------
    # 4. MOCK APPROVED CANONICAL GRAPH
    # --------------------------------------------------

    canonical_graph = Mock()

    canonical_graph.approval_status = "approved"

    # --------------------------------------------------
    # 5. MOCK SUGGESTION WORKFLOW
    # --------------------------------------------------

    mock_workflow = Mock()

    expected_result = SuggestionGraph(
        project_id="integration-test",
        suggestions=[],
    )

    mock_workflow.generate_suggestions.return_value = expected_result

    story_rag._suggestion_workflow = mock_workflow

    # --------------------------------------------------
    # 6. GENERATE SUGGESTIONS
    # --------------------------------------------------

    result = story_rag.generate_suggestions(
        story_context=(
            "The protagonist enters an unfamiliar forest "
            "while searching for a missing friend."
        ),
        max_suggestions=3,
        inspiration_top_k=5,
    )

    # --------------------------------------------------
    # 7. VERIFY INSPIRATION SEARCH
    # --------------------------------------------------

    mock_inspiration_service.search.assert_called_once()

    search_arguments = mock_inspiration_service.search.call_args.kwargs

    assert "forest" in search_arguments["query"].lower()

    print("PASS: Inspiration search was triggered.")

    # --------------------------------------------------
    # 8. VERIFY INSPIRATION REACHED WORKFLOW
    # --------------------------------------------------

    workflow_arguments = mock_workflow.generate_suggestions.call_args.kwargs

    retrieved_references = workflow_arguments["inspiration_results"]

    assert len(retrieved_references) == 1

    assert retrieved_references[0]["record"].id == inspiration_record.id

    print("PASS: Retrieved inspiration reached suggestion workflow.")

    # --------------------------------------------------
    # 9. VERIFY STORY CONTEXT
    # --------------------------------------------------

    assert workflow_arguments["story_context"].startswith("The protagonist")

    assert workflow_arguments["max_suggestions"] == 3

    print("PASS: Story context and suggestion limit preserved.")

    # --------------------------------------------------
    # 10. VERIFY RESULT
    # --------------------------------------------------

    assert result == expected_result

    print("PASS: Suggestion result returned successfully.")

    story_rag.close()

    print("\nAll Story Intelligence + Inspiration integration checks passed!")


if __name__ == "__main__":
    main()
