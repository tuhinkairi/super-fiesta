
from modules.story_intelligence.types import (
    StoryInput,
    StoryProcessingResult,
)

from modules.story_intelligence.knowledge_graph.entity_extractor import (
    EntityExtractor,
)

from modules.story_intelligence.knowledge_graph.entity_resolver import (
    EntityResolver,
)

from modules.story_intelligence.knowledge_graph.relation_extractor import (
    RelationExtractor,
)

from modules.story_intelligence.knowledge_graph.event_extractor import (
    EventExtractor,
)

from modules.story_intelligence.knowledge_graph.timeline_builder import (
    TimelineBuilder,
)

from modules.story_intelligence.knowledge_graph.graph_builder import (
    GraphBuilder,
)


class StoryWorkflow:
    """
    Coordinates individual story processing components.
    """

    def __init__(
        self,
        entity_extractor: EntityExtractor,
        relation_extractor: RelationExtractor,
        event_extractor: EventExtractor,
    ):

        self.entity_extractor = entity_extractor
        self.relation_extractor = relation_extractor
        self.event_extractor = event_extractor

    def process(self, story_input: StoryInput) -> StoryProcessingResult:
        """
        Execute the complete story understanding workflow.
        """

        if not story_input.story_text.strip():
            raise ValueError("Story text cannot be empty.")

        print("\n[1/6] Extracting characters...")

        raw_characters = (
            self.entity_extractor.extract_characters(
                story_input.story_text
            )
        )

        print("\n[2/6] Resolving character identities...")

        characters = EntityResolver.resolve(
            raw_characters
        )

        print("\n[3/6] Extracting relationships...")

        relationships = (
            self.relation_extractor.extract_relationships(
                story_text=story_input.story_text,
                characters=characters,
            )
        )

        print("\n[4/6] Extracting story events...")

        events = self.event_extractor.extract_events(
            story_text=story_input.story_text,
            characters=characters,
            chapter_number=story_input.chapter_number,
        )

        print("\n[5/6] Constructing timeline...")

        timeline = TimelineBuilder.build(events)

        print("\n[6/6] Building canonical knowledge graph...")

        knowledge_graph = GraphBuilder.build(
            characters=characters,
            relationships=relationships,
            events=events,
            project_id=story_input.project_id,
        )

        return StoryProcessingResult(
            project_id=story_input.project_id,
            characters=characters,
            relationships=relationships,
            events=events,
            timeline=timeline,
            knowledge_graph=knowledge_graph,
            processing_status="completed",
        )
