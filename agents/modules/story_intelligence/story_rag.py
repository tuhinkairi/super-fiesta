
from modules.story_intelligence.pipeline.orchestrator import (
    StoryOrchestrator,
)

from modules.story_intelligence.types import (
    StoryInput,
    StoryProcessingResult,
)

from modules.story_intelligence.llm.llm_client import (
    LLMClient,
)

from modules.story_intelligence.models.graph import (
    StoryKnowledgeGraph,
)

from modules.story_intelligence.models.suggestion import (
    SuggestionGraph,
    SuggestionApprovalResult,
    StorySuggestion,
)

from modules.story_intelligence.suggestion_graph.suggestion_workflow import (
    SuggestionWorkflow,
)

from modules.inspiration_ingestion.service import (
    InspirationService,
)


class StoryRAG:
    """
    Public orchestration interface for the Story Intelligence module.

    Coordinates:
    1. Story processing
    2. Canonical graph approval
    3. Inspiration ingestion and retrieval
    4. Suggestion generation
    5. Suggestion approval and rejection
    """

    def __init__(
        self,
        llm_client: LLMClient | None = None,
        inspiration_service: InspirationService | None = None,
    ):
        # Track ownership of the shared LLM client.
        self._owns_llm_client = llm_client is None

        # Create one shared LLM client.
        self.llm_client = (
            llm_client
            if llm_client is not None
            else LLMClient()
        )

        # Create the story orchestrator.
        self.orchestrator = StoryOrchestrator(
            llm_client=self.llm_client
        )

        # Suggestion workflow is created after graph approval.
        self._suggestion_workflow = None

        # Store the latest story processing result.
        self.last_result: StoryProcessingResult | None = None

        # Track ownership of the inspiration service.
        self._owns_inspiration_service = inspiration_service is None

        # Create inspiration service using the same LLM client.
        self.inspiration_service = (
            inspiration_service
            if inspiration_service is not None
            else InspirationService(
                llm_client=self.llm_client
            )
        )

    # --------------------------------------------------
    # STORY PROCESSING
    # --------------------------------------------------

    def process_story(
        self,
        project_id: str,
        story_text: str,
        chapter_number: int | None = None,
    ) -> StoryProcessingResult:
        """
        Process story text and generate its canonical graph.

        The generated graph remains pending until explicitly
        approved by the author.
        """

        story_input = StoryInput(
            project_id=project_id,
            story_text=story_text,
            chapter_number=chapter_number,
        )

        # A new story invalidates any previous suggestion workflow.
        if self._suggestion_workflow is not None:
            self._suggestion_workflow.close()
            self._suggestion_workflow = None

        result = self.orchestrator.process_story(story_input)

        self.last_result = result

        return result

    # --------------------------------------------------
    # CANONICAL GRAPH APPROVAL
    # --------------------------------------------------

    def approve_canonical_graph(self) -> StoryKnowledgeGraph:
        """
        Explicitly approve the latest processed canonical graph.

        This method represents the author's approval action.
        It does not automatically approve suggestions.
        """

        if self.last_result is None:
            raise RuntimeError(
                "No story has been processed. "
                "Process a story before approving its graph."
            )

        canonical_graph = self.last_result.knowledge_graph

        if canonical_graph.approval_status == "approved":
            raise RuntimeError(
                "The canonical graph has already been approved."
            )

        # Create an approved copy without mutating the original graph.
        approved_graph = canonical_graph.model_copy(
            update={"approval_status": "approved"},
            deep=True,
        )

        # Replace the graph inside the processing result.
        self.last_result = self.last_result.model_copy(
            update={"knowledge_graph": approved_graph},
            deep=True,
        )

        return approved_graph

    # --------------------------------------------------
    # INSPIRATION INGESTION
    # --------------------------------------------------

    def add_inspiration_file(self, file_path: str):
        """
        Add a local inspiration file.
        """

        return self.inspiration_service.add_file(file_path)

    def add_inspiration_url(self, url: str):
        """
        Add a web URL as inspiration.
        """

        return self.inspiration_service.add_url(url)

    def search_inspiration(
        self,
        query: str,
        top_k: int = 5,
    ):
        """
        Search the inspiration library semantically.
        """

        return self.inspiration_service.search(
            query=query,
            top_k=top_k,
        )

    def list_inspirations(self):
        """
        Return all stored inspiration records.
        """

        return self.inspiration_service.list_all()

    def get_inspiration(self, record_id: str):
        """
        Retrieve one inspiration record.
        """

        return self.inspiration_service.get(record_id)

    # --------------------------------------------------
    # SUGGESTION WORKFLOW
    # --------------------------------------------------

    def start_suggestion_workflow(
        self,
        canonical_graph: StoryKnowledgeGraph,
        suggestion_graph: SuggestionGraph | None = None,
    ):
        """
        Start suggestion generation using an approved graph.
        """

        if canonical_graph.approval_status != "approved":
            raise ValueError(
                "Canonical graph must be approved before "
                "starting the suggestion workflow."
            )

        if self._suggestion_workflow is not None:
            self._suggestion_workflow.close()

        self._suggestion_workflow = SuggestionWorkflow(
            canonical_graph=canonical_graph,
            suggestion_graph=suggestion_graph,
            llm_client=self.llm_client,
        )

        return self._suggestion_workflow

    def generate_suggestions(
        self,
        story_context: str,
        max_suggestions: int = 3,
        inspiration_top_k: int = 5,
    ):
        """
        Generate creative suggestions using the approved
        canonical graph and relevant inspiration references.
        """

        if self._suggestion_workflow is None:
            raise RuntimeError(
                "Start the suggestion workflow first."
            )

        if not story_context or not story_context.strip():
            raise ValueError(
                "Story context cannot be empty."
            )

        if inspiration_top_k < 1:
            raise ValueError(
                "inspiration_top_k must be at least 1."
            )

        # Search inspiration only when the library contains records.
        inspiration_results = []

        if self.inspiration_service.metadata_store.count() > 0:
            inspiration_results = self.inspiration_service.search(
                query=story_context,
                top_k=inspiration_top_k,
            )

        return self._suggestion_workflow.generate_suggestions(
            story_context=story_context,
            max_suggestions=max_suggestions,
            inspiration_results=inspiration_results,
        )

    # --------------------------------------------------
    # SUGGESTION RETRIEVAL
    # --------------------------------------------------

    def get_suggestion(
        self,
        suggestion_id: str,
    ) -> StorySuggestion | None:
        """
        Retrieve a suggestion by its ID.
        """

        if self._suggestion_workflow is None:
            raise RuntimeError(
                "Suggestion workflow has not been started."
            )

        return self._suggestion_workflow.get_suggestion(
            suggestion_id
        )

    def list_suggestions(
        self,
        status: str | None = None,
    ) -> list[StorySuggestion]:
        """
        Return all suggestions or filter them by status.
        """

        if self._suggestion_workflow is None:
            raise RuntimeError(
                "Suggestion workflow has not been started."
            )

        return self._suggestion_workflow.list_suggestions(
            status=status
        )

    # --------------------------------------------------
    # SUGGESTION APPROVAL
    # --------------------------------------------------

    def approve_suggestion(
        self,
        suggestion_id: str,
        override_warnings: bool = False,
        override_reason: str = "",
    ) -> SuggestionApprovalResult:
        """
        Approve a proposed suggestion.

        Critical guardrail findings cannot be overridden.
        Warning findings require an explicit override reason.
        """

        if self._suggestion_workflow is None:
            raise RuntimeError(
                "Suggestion workflow has not been started."
            )

        return self._suggestion_workflow.approve_suggestion(
            suggestion_id=suggestion_id,
            override_warnings=override_warnings,
            override_reason=override_reason,
        )

    def reject_suggestion(
        self,
        suggestion_id: str,
        reason: str = "",
    ) -> SuggestionGraph:
        """
        Reject a proposed suggestion.
        """

        if self._suggestion_workflow is None:
            raise RuntimeError(
                "Suggestion workflow has not been started."
            )

        return self._suggestion_workflow.reject_suggestion(
            suggestion_id=suggestion_id,
            reason=reason,
        )

    # --------------------------------------------------
    # GRAPH ACCESS
    # --------------------------------------------------

    @property
    def canonical_graph(self) -> StoryKnowledgeGraph | None:
        """
        Return the current canonical graph.
        """

        if self._suggestion_workflow is not None:
            return self._suggestion_workflow.canonical_graph

        if self.last_result is not None:
            return self.last_result.knowledge_graph

        return None

    @property
    def suggestion_graph(self) -> SuggestionGraph | None:
        """
        Return the current suggestion graph.
        """

        if self._suggestion_workflow is None:
            return None

        return self._suggestion_workflow.suggestion_graph

    # --------------------------------------------------
    # RESOURCE MANAGEMENT
    # --------------------------------------------------

    def close(self):
        """
        Close owned resources safely.
        """

        if self._suggestion_workflow is not None:
            self._suggestion_workflow.close()
            self._suggestion_workflow = None

        self.orchestrator.close()

        if self._owns_inspiration_service:
            self.inspiration_service.close()

        if self._owns_llm_client:
            self.llm_client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
