
from pydantic import BaseModel, Field

from modules.story_intelligence.llm.llm_client import LLMClient


class TestAnalysis(BaseModel):
    summary: str = Field(description="A short summary.")
    keywords: list[str] = Field(description="Important keywords.")


def main():

    client = LLMClient()

    try:
        # Test 1: Structured text generation.
        print("Testing Gemini structured text generation...")

        result = client.generate_structured(
            prompt=(
                "Analyze this idea: "
                "Two childhood friends reunite after ten years "
                "and start a journey to find a lost library. "
                "Return a short summary and 3-5 keywords."
            ),
            response_schema=TestAnalysis,
        )

        print("\nStructured generation passed!")
        print("Summary:", result.summary)
        print("Keywords:", result.keywords)

        assert result.summary
        assert len(result.keywords) > 0

        # Test 2: Real embedding generation.
        print("\nTesting Gemini embedding generation...")

        embedding = client.generate_embedding(
            "A mysterious story about friendship and discovery."
        )

        print("Embedding generation passed!")
        print("Embedding dimensions:", len(embedding))

        assert len(embedding) == 768

        print("\nAll live Gemini text checks passed!")

    finally:
        client.close()


if __name__ == "__main__":
    main()
