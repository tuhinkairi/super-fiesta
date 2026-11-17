
from pydantic import BaseModel, Field

from modules.story_intelligence.models.character import (
    CharacterExtractionResult,
)

from modules.story_intelligence.models.relationship import (
    RelationshipExtractionResult,
)

from modules.story_intelligence.models.event import (
    EventExtractionResult,
)

from modules.story_intelligence.models.timeline import (
    TimelineResult,
)

from modules.story_intelligence.models.graph import (
    StoryKnowledgeGraph,
)


class StoryInput(BaseModel):
    """
    Input provided to the Story Intelligence module.
    """

    project_id: str

    story_text: str = Field(
        min_length=1,
        description="Original story text to analyze.",
    )

    chapter_number: int | None = Field(
        default=None,
        ge=1,
    )


class StoryProcessingResult(BaseModel):
    """
    Complete output of the story analysis pipeline.
    """

    project_id: str

    characters: CharacterExtractionResult

    relationships: RelationshipExtractionResult

    events: EventExtractionResult

    timeline: TimelineResult

    knowledge_graph: StoryKnowledgeGraph

    processing_status: str = "completed"
