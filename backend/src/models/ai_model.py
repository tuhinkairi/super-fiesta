"""Adapters from backend operations to the AI modules in ``modules/``."""

from __future__ import annotations
import sys
from pathlib import Path
from modules.story_intelligence.story_rag import StoryRAG

# ``uvicorn main:app`` is commonly launched from ``backend/``. Add the repo
# root so the sibling top-level ``modules`` package remains importable there.
REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))


class AIModel:
    """Own one StoryRAG workflow per project for the current API process."""

    def __init__(self) -> None:
        self._projects: dict[str, StoryRAG] = {}

    def _get_project(self, project_id: str) -> StoryRAG:
        if project_id not in self._projects:
            try:
                from modules.story_intelligence.story_rag import StoryRAG

                self._projects[project_id] = StoryRAG()
            except (ImportError, ValueError) as exc:
                raise RuntimeError(
                    "AI is not configured. Install the AI module dependencies and set GEMINI_API_KEY."
                ) from exc
        return self._projects[project_id]

    def analyze_story(
        self, project_id: str, story_text: str, chapter_number: int | None = None
    ):
        return self._get_project(project_id).process_story(
            project_id=project_id, story_text=story_text, chapter_number=chapter_number
        )

    def approve_graph(self, project_id: str):
        rag = self._require_project(project_id)
        graph = rag.approve_canonical_graph()
        rag.start_suggestion_workflow(graph)
        return graph

    def suggest(self, project_id: str, story_context: str, limit: int):
        return self._require_project(project_id).generate_suggestions(
            story_context=story_context, max_suggestions=limit
        )

    def add_inspiration(self, project_id: str, file_path: str):
        return self._get_project(project_id).add_inspiration_file(file_path)

    def search_inspiration(self, project_id: str, query: str, limit: int):
        return self._get_project(project_id).search_inspiration(query, limit)

    def _require_project(self, project_id: str) -> StoryRAG:
        rag = self._projects.get(project_id)
        if rag is None or rag.last_result is None:
            raise LookupError("Analyze a story for this project first.")
        return rag

    def close(self) -> None:
        for rag in self._projects.values():
            rag.close()
        self._projects.clear()
                                                                                                                