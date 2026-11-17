from modules.story_intelligence.llm.llm_client import LLMClient

from modules.story_intelligence.types import (
    StoryInput,
    StoryProcessingResult,
)

from modules.story_intelligence.knowledge_graph.entity_extractor import (
    EntityExtractor,
)

from modules.story_intelligence.knowledge_graph.relation_extractor import (
    RelationExtractor,
)

from modules.story_intelligence.knowledge_graph.event_extractor import (
    EventExtractor,
)

from modules.story_intelligence.pipeline.workflow import (
    StoryWorkflow,
)


class StoryOrchestrator:
    """
    Main coordinator for the Story Intelligence module.

    Creates shared dependencies and starts the workflow.
    """

    def __init__(self, llm_client=None):

        # Track whether this orchestrator owns the client.
        self._owns_client = llm_client is None

        # Create one shared LLM client.
        self.llm_client = llm_client if llm_client is not None else LLMClient()

        # Inject the same client into every extractor.
        self.entity_extractor = EntityExtractor(llm_client=self.llm_client)

        self.relation_extractor = RelationExtractor(llm_client=self.llm_client)

        self.event_extractor = EventExtractor(llm_client=self.llm_client)

        # Create the complete workflow.
        self.workflow = StoryWorkflow(
            entity_extractor=self.entity_extractor,
            relation_extractor=self.relation_extractor,
            event_extractor=self.event_extractor,
        )

    def process_story(
        self,
        story_input: StoryInput,
    ) -> StoryProcessingResult:
        """
        Public method for processing a story.
        """

        return self.workflow.process(story_input)

    def close(self):
        """
        Close the shared LLM client only when owned.
        """

        if self._owns_client:
            self.llm_client.close()
