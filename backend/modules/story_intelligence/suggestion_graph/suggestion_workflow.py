from modules.story_intelligence.models.graph import StoryKnowledgeGraph
from modules.story_intelligence.models.suggestion import (
    StorySuggestion,
    SuggestionGraph,
    SuggestionApprovalResult,
)

from modules.story_intelligence.llm.llm_client import LLMClient
from modules.story_intelligence.suggestion_graph.suggestion_generator import (
    SuggestionGenerator,
)
from modules.story_intelligence.suggestion_graph.suggestion_builder import (
    SuggestionBuilder,
)
from modules.story_intelligence.suggestion_graph.guardrail_engine import (
    GuardrailEngine,
)
from modules.story_intelligence.suggestion_graph.approval_manager import (
    ApprovalManager,
)


class SuggestionWorkflow:
    """
    Coordinates the complete story suggestion workflow.

    Workflow:
        1. Generate hypothetical suggestions.
        2. Optionally use retrieved inspiration references.
        3. Validate and add suggestions to the suggestion graph.
        4. Run guardrail checks.
        5. Allow the author to approve or reject suggestions.

    Canonical story facts are never modified during generation
    or rejection. Approval creates a new canonical graph version.

    Inspiration references are creative material only.
    They never automatically become canonical story facts.
    """

    def __init__(
        self,
        canonical_graph: StoryKnowledgeGraph,
        llm_client: LLMClient | None = None,
        suggestion_graph: SuggestionGraph | None = None,
    ):
        if canonical_graph.approval_status != "approved":
            raise ValueError(
                "Suggestion workflow requires an approved canonical graph."
            )

        self.canonical_graph = canonical_graph

        if suggestion_graph is None:
            suggestion_graph = SuggestionGraph(
                project_id=canonical_graph.project_id,
                suggestions=[],
            )

        if suggestion_graph.project_id != canonical_graph.project_id:
            raise ValueError(
                "Canonical and suggestion graphs must belong " "to the same project."
            )

        self.suggestion_graph = suggestion_graph

        # Generator owns the client only when one isn't injected.
        self.generator = SuggestionGenerator(llm_client=llm_client)

    def generate_suggestions(
        self,
        story_context: str,
        max_suggestions: int = 3,
        inspiration_results: list[dict] | None = None,
    ) -> SuggestionGraph:
        """
        Generate, guardrail-check, and store new suggestions.

        Optional inspiration results provide creative context
        without changing canonical story facts.
        """

        # Step 1: Generate hypothetical suggestions.
        generated_graph = self.generator.generate_suggestions(
            canonical_graph=self.canonical_graph,
            story_context=story_context,
            max_suggestions=max_suggestions,
            inspiration_results=inspiration_results,
        )

        # Step 2: Prepare the builder using the current suggestion graph.
        builder = SuggestionBuilder(
            canonical_graph=self.canonical_graph,
            suggestion_graph=self.suggestion_graph,
        )

        guardrail_engine = GuardrailEngine(canonical_graph=self.canonical_graph)

        # Step 3: Validate each suggestion and add it separately.
        for suggestion in generated_graph.suggestions:

            validated_suggestion = guardrail_engine.validate(suggestion)

            self.suggestion_graph = builder.add_suggestion(validated_suggestion)

        return self.suggestion_graph

    def get_suggestion(
        self,
        suggestion_id: str,
    ) -> StorySuggestion:
        """Retrieve a suggestion by its ID."""

        for suggestion in self.suggestion_graph.suggestions:
            if suggestion.suggestion_id == suggestion_id:
                return suggestion

        raise ValueError(f"Suggestion not found: {suggestion_id}")

    def list_suggestions(
        self,
        status: str | None = None,
    ) -> list[StorySuggestion]:
        """List all suggestions or filter by status."""

        if status is None:
            return list(self.suggestion_graph.suggestions)

        return [
            suggestion
            for suggestion in self.suggestion_graph.suggestions
            if suggestion.status == status
        ]

    def _refresh_guardrail_findings(
        self,
        suggestion: StorySuggestion,
    ) -> StorySuggestion:
        """
        Recheck the suggestion against the latest canonical graph.

        This prevents approval from relying on stale guardrail results.
        """

        guardrail_engine = GuardrailEngine(canonical_graph=self.canonical_graph)

        refreshed_suggestion = guardrail_engine.validate(suggestion)

        updated_suggestions = [
            (
                refreshed_suggestion
                if item.suggestion_id == suggestion.suggestion_id
                else item
            )
            for item in self.suggestion_graph.suggestions
        ]

        self.suggestion_graph = self.suggestion_graph.model_copy(
            update={
                "suggestions": updated_suggestions,
            }
        )

        return refreshed_suggestion

    def approve_suggestion(
        self,
        suggestion_id: str,
        override_warnings: bool = False,
        override_reason: str | None = None,
    ) -> SuggestionApprovalResult:
        """
        Revalidate and approve a proposed suggestion.

        Warning overrides require explicit author permission
        and a reason. Critical findings cannot be overridden.
        """

        suggestion = self.get_suggestion(suggestion_id)

        if suggestion.status != "proposed":
            raise ValueError("Only proposed suggestions can be approved.")

        # Refresh findings before the approval decision.
        self._refresh_guardrail_findings(suggestion)

        manager = ApprovalManager(
            canonical_graph=self.canonical_graph,
            suggestion_graph=self.suggestion_graph,
        )

        result = manager.approve_suggestion(
            suggestion_id=suggestion_id,
            override_warnings=override_warnings,
            override_reason=override_reason,
        )

        # Save the returned graph versions as workflow state.
        self.canonical_graph = result.canonical_graph
        self.suggestion_graph = result.suggestion_graph

        return result

    def reject_suggestion(
        self,
        suggestion_id: str,
        reason: str = "",
    ) -> SuggestionApprovalResult:
        """
        Reject a proposed suggestion without changing
        the canonical knowledge graph.
        """

        manager = ApprovalManager(
            canonical_graph=self.canonical_graph,
            suggestion_graph=self.suggestion_graph,
        )

        result = manager.reject_suggestion(
            suggestion_id=suggestion_id,
            reason=reason,
        )

        self.canonical_graph = result.canonical_graph
        self.suggestion_graph = result.suggestion_graph

        return result

    def close(self):
        """Close the generator and its owned LLM client."""

        self.generator.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
