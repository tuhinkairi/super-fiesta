"""Request schemas for AI endpoints."""

from pydantic import BaseModel, Field
from typing import Optional

class StoryAnalysisRequest(BaseModel):
    project_id: Optional[str] = Field(min_length=1, max_length=120)
    story_text: str = Field(min_length=1)
    chapter_number: int | None = Field(default=None, ge=1)


class SuggestionRequest(BaseModel):
    story_context: str = Field(min_length=1)
    limit: int = Field(default=3, ge=1, le=10)


class InspirationSearchRequest(BaseModel):
    query: str = Field(min_length=1)
    limit: int = Field(default=5, ge=1, le=20)
