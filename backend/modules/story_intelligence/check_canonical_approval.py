from modules.story_intelligence.story_rag import StoryRAG


def main():
    print("Testing canonical graph approval...")

    rag = StoryRAG()

    try:
        # Simulate a processed result without calling Gemini.
        from modules.story_intelligence.types import StoryProcessingResult
        from modules.story_intelligence.models.graph import StoryKnowledgeGraph

        pending_graph = StoryKnowledgeGraph(
            project_id="approval-test-001",
            approval_status="pending",
        )

        rag.last_result = StoryProcessingResult.model_construct(
            project_id="approval-test-001",
            characters=None,
            relationships=None,
            events=None,
            timeline=None,
            knowledge_graph=pending_graph,
            processing_status="completed",
        )

        print("\n[1/4] Checking initial approval status...")

        assert rag.canonical_graph.approval_status == "pending"
        print("PASS: Graph initially pending.")

        print("\n[2/4] Approving canonical graph...")

        approved_graph = rag.approve_canonical_graph()

        assert approved_graph.approval_status == "approved"
        print("PASS: Graph approved.")

        print("\n[3/4] Checking stored result...")

        assert rag.last_result.knowledge_graph.approval_status == "approved"
        print("PASS: Updated graph stored in StoryProcessingResult.")

        print("\n[4/4] Checking duplicate approval protection...")

        try:
            rag.approve_canonical_graph()
            raise AssertionError("Duplicate approval was not blocked.")
        except RuntimeError as exc:
            assert "already been approved" in str(exc)
            print("PASS: Duplicate approval blocked.")

        print("\nCANONICAL APPROVAL TEST PASSED")

    finally:
        rag.close()


if __name__ == "__main__":
    main()
