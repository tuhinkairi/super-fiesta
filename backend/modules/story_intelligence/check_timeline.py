from modules.story_intelligence.models.event import (
    StoryEvent,
    EventExtractionResult,
)

from modules.story_intelligence.knowledge_graph.timeline_builder import (
    TimelineBuilder,
)


def main():

    # Deliberately provide events in the wrong order.
    events = EventExtractionResult(
        events=[
            StoryEvent(
                title="Arjun confronts Rohan",
                participants=["Arjun", "Rohan"],
                chapter_number=2,
                sequence_index=2,
                chronology_basis="narrative_order",
            ),
            StoryEvent(
                title="Arjun enters the palace",
                participants=["Arjun"],
                chapter_number=1,
                sequence_index=1,
                chronology_basis="narrative_order",
            ),
            StoryEvent(
                title="Maya reveals Rohan's secret",
                participants=["Maya", "Rohan"],
                chapter_number=2,
                sequence_index=1,
                chronology_basis="narrative_order",
            ),
        ]
    )

    # Build the timeline.
    timeline = TimelineBuilder.build(events)

    print("Timeline construction successful!")

    print("\nOrdered story events:\n")

    for event in timeline.events:
        print(
            f"Chapter {event.chapter_number} | "
            f"Sequence {event.sequence_index} | "
            f"{event.title}"
        )

    print("\nOrdering method:", timeline.ordering_method)
    print("Chronology verified:", timeline.chronology_verified)

    print("\nComplete timeline JSON:\n")

    print(timeline.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
