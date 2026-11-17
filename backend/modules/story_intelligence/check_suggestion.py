from modules.story_intelligence.models.suggestion import (
    StorySuggestion,
    SuggestionGraph,
    SuggestionFinding,
)


def main():

    suggestion = StorySuggestion(
        title="Maya's secret alliance",
        description=(
            "Maya may secretly be working with " "the enemy to protect Arjun."
        ),
        suggestion_type="plot_twist",
        rationale=(
            "This could introduce a moral conflict " "and an unexpected revelation."
        ),
        source_evidence=["His sister Maya was waiting for him."],
        status="proposed",
    )

    # Add a sample guardrail finding.
    suggestion.guardrail_findings.append(
        SuggestionFinding(
            rule_id="EXAMPLE_WARNING",
            severity="advisory",
            message="This is a sample validation finding.",
        )
    )

    suggestion_graph = SuggestionGraph(
        project_id="test-project-001",
        suggestions=[suggestion],
    )

    print("Suggestion model working!")

    print("\nNumber of suggestions:")
    print(len(suggestion_graph.suggestions))

    print("\nSuggestion status:")
    print(suggestion_graph.suggestions[0].status)

    print("\nSuggestion JSON:\n")
    print(suggestion_graph.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
