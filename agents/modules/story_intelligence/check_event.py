
from modules.story_intelligence.models.event import (
    StoryEvent,
    EventEvidence,
    EventExtractionResult,
)


event = StoryEvent(
    title="Arjun enters the palace",
    description="Arjun enters the palace.",
    participants=["Arjun"],
    sequence_index=1,
    chronology_basis="narrative_order",
    evidence=[
        EventEvidence(
            quote="Arjun entered the palace.",
            evidence_type="explicit",
        )
    ],
)


result = EventExtractionResult(
    events=[event]
)

print("Event model working!")
print(result.model_dump_json(indent=2))
