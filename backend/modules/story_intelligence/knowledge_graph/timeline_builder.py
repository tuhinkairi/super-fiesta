from modules.story_intelligence.models.event import (
    EventExtractionResult,
)

from modules.story_intelligence.models.timeline import (
    TimelineResult,
)


class TimelineBuilder:
    """
    Organizes extracted story events into a timeline.

    Uses chapter numbers and narrative sequence.
    Does not invent or automatically interpret dates.
    """

    @staticmethod
    def build(
        extraction_result: EventExtractionResult,
    ) -> TimelineResult:

        events = extraction_result.events

        if not events:
            return TimelineResult(
                events=[],
                ordering_method="input_order",
                ordering_warnings=[],
                chronology_verified=False,
            )

        # Check that event IDs are unique.
        event_ids = [event.event_id for event in events]

        if len(event_ids) != len(set(event_ids)):
            raise ValueError("Duplicate event IDs found in timeline.")

        warnings = []

        # Separate events with known chapters from
        # events whose chapter is not known.
        known_chapter_events = []
        unknown_chapter_events = []

        for original_index, event in enumerate(events):

            if event.chapter_number is not None:
                known_chapter_events.append((original_index, event))
            else:
                unknown_chapter_events.append((original_index, event))

                warnings.append(f"Chapter number unknown for event: {event.title}")

            # Explicit time references are preserved,
            # but this builder does not interpret their dates.
            if event.chronology_basis == "explicit_time":
                warnings.append(
                    f"Explicit time reference not normalized "
                    f"for event: {event.title}"
                )

            if event.chronology_basis == "unknown":
                warnings.append(f"Chronology is uncertain for event: {event.title}")

        # Sort chapter-known events first.
        # Use original position to maintain stable ordering
        # when chapter and sequence are identical.
        known_chapter_events.sort(
            key=lambda item: (
                item[1].chapter_number,
                item[1].sequence_index,
                item[0],
            )
        )

        # Preserve original relative order when the chapter
        # is unknown, because sequence indices may restart.
        unknown_chapter_events.sort(key=lambda item: item[0])

        ordered_events = [event for _, event in known_chapter_events]

        ordered_events.extend(event for _, event in unknown_chapter_events)

        # Identify the ordering method.
        if unknown_chapter_events:
            ordering_method = "narrative_sequence"
        elif known_chapter_events:
            ordering_method = "chapter_and_sequence"
        else:
            ordering_method = "input_order"

        return TimelineResult(
            events=ordered_events,
            ordering_method=ordering_method,
            ordering_warnings=list(dict.fromkeys(warnings)),
            chronology_verified=False,
        )
