from modules.story_intelligence.story_rag import StoryRAG

STORY_TEXT = """
Anaya is a young cartographer who returns to her coastal hometown
after receiving a letter from her childhood friend, Kabir.

The letter reveals that Kabir has discovered an old map hidden in
the town's abandoned lighthouse. He believes the map leads to a
forgotten underground library.

Anaya meets Kabir at the lighthouse. They discover that the map
contains a series of symbols that neither of them can understand.
They ask Meera, a local historian and Anaya's former teacher, for help.

Meera recognizes the symbols as clues left by the town's founder.
Together, the three of them decode the map and discover a concealed
entrance beneath the lighthouse.

Inside, they find the forgotten library and a journal describing
the town's history. However, the journal's final pages have been torn out.
Anaya decides that finding those missing pages will be their next mission.
"""


class EmptyMetadataStore:
    def count(self):
        return 0


class EmptyInspirationService:
    def __init__(self):
        self.metadata_store = EmptyMetadataStore()

    def close(self):
        pass


def main():
    story_rag = StoryRAG(inspiration_service=EmptyInspirationService())

    try:
        # 1. Live story processing: 3 Gemini requests.
        print("\n[1/4] Processing story with Gemini...")

        result = story_rag.process_story(
            project_id="live-story-intelligence-test",
            story_text=STORY_TEXT,
            chapter_number=1,
        )

        canonical_graph = result.knowledge_graph

        print("\nStory processing completed.")
        print("Project ID:", result.project_id)
        print("Characters:", len(result.characters.characters))
        print("Relationships:", len(result.relationships.relationships))
        print("Events:", len(result.events.events))
        print("Timeline events:", len(result.timeline.events))
        print("Graph nodes:", len(canonical_graph.nodes))
        print("Graph edges:", len(canonical_graph.edges))
        print("Graph approval status:", canonical_graph.approval_status)

        assert canonical_graph.approval_status == "pending"

        print("PASS: Story processing completed.")
        print("PASS: Original graph remains pending.")

        # 2. Simulate author approval on an isolated copy.
        # No Gemini request.
        print("\n[2/4] Preparing approved graph copy...")

        approved_graph = canonical_graph.model_copy(
            update={"approval_status": "approved"},
            deep=True,
        )

        assert approved_graph.approval_status == "approved"
        assert canonical_graph.approval_status == "pending"

        print("PASS: Separate approved graph created.")
        print("PASS: Original graph remains unchanged.")

        # 3. Start suggestion workflow.
        # No Gemini request.
        print("\n[3/4] Starting suggestion workflow...")

        story_rag.start_suggestion_workflow(approved_graph)

        print("PASS: Suggestion workflow initialized.")

        # 4. Live suggestion generation: 1 Gemini request.
        print("\n[4/4] Generating suggestions with Gemini...")

        suggestion_graph = story_rag.generate_suggestions(
            story_context=STORY_TEXT,
            max_suggestions=2,
            inspiration_top_k=3,
        )

        suggestions = suggestion_graph.suggestions

        print("\nSuggestions generated:", len(suggestions))

        if not suggestions:
            raise AssertionError("No suggestions were generated.")

        for index, suggestion in enumerate(suggestions, start=1):
            print(f"\nSuggestion {index}")
            print("Title:", suggestion.title)
            print("Type:", suggestion.suggestion_type)
            print("Status:", suggestion.status)
            print("Rationale:", suggestion.rationale)

        assert all(suggestion.status == "proposed" for suggestion in suggestions)

        assert canonical_graph.approval_status == "pending"

        print("\nPASS: Suggestions generated.")
        print("PASS: Suggestions remain proposed.")
        print("PASS: Original graph remains pending.")

        print("\n========================================")
        print("LIVE STORY INTELLIGENCE TEST PASSED")
        print("========================================")
        print("Expected Gemini requests: 4")
        print("Story extraction: 3")
        print("Suggestion generation: 1")
        print("Graph construction and approval: 0")

    finally:
        story_rag.close()


if __name__ == "__main__":
    main()
