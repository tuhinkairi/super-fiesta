from modules.inspiration_ingestion.types import InspirationRecord


def main():
    record = InspirationRecord(
        file_name="story_ideas.pdf",
        content_type="pdf",
        extracted_text="A story about friendship and betrayal.",
        summary="A dramatic story about two friends.",
        keywords=["friendship", "betrayal"],
        themes=["trust", "relationships"],
        mood_tags=["emotional", "dramatic"],
        provenance={
            "original_file": "story_ideas.pdf",
            "uploaded_by": "user",
        },
    )

    print("Inspiration record created successfully!")
    print("\nRecord ID:", record.id)
    print("File name:", record.file_name)
    print("Content type:", record.content_type)
    print("Summary:", record.summary)
    print("Keywords:", record.keywords)
    print("Uploaded at:", record.uploaded_at)

    # Validation checks.
    assert record.id
    assert record.content_type == "pdf"
    assert len(record.keywords) == 2
    assert record.embedding is None

    print("\nAll data model checks passed!")


if __name__ == "__main__":
    main()
