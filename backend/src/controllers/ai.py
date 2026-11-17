from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, HTTPException, Request, UploadFile, status
from fastapi.concurrency import run_in_threadpool

from src.models.ai_schemas import InspirationSearchRequest, StoryAnalysisRequest, SuggestionRequest
from src.services.ai_services import get_ai_model
import os


project_id = os.getenv("GEMINI_PROJECT_ID")
router = APIRouter(prefix="/ai", tags=["AI tools"])


def _handle_error(exc: Exception):
    if isinstance(exc, LookupError):
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if isinstance(exc, RuntimeError) and "not configured" in str(exc):
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    if isinstance(exc, (ValueError, FileNotFoundError)):
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    raise HTTPException(status_code=502, detail=f"AI operation failed: {exc}") from exc


@router.post("/stories/analyze")
async def analyze_story(body: StoryAnalysisRequest, request: Request):
    try:
        model = get_ai_model(request.app)
        result = await run_in_threadpool(model.analyze_story, body.project_id, body.story_text, body.chapter_number)
        return result.model_dump(mode="json")
    except Exception as exc:
        _handle_error(exc)


@router.post(f"/stories/{project_id}/graph/approve")
async def approve_story_graph(request: Request):
    try:
        graph = await run_in_threadpool(get_ai_model(request.app).approve_graph, project_id)
        return graph.model_dump(mode="json")
    except Exception as exc:
        _handle_error(exc)


@router.post(f"/stories/{project_id}/suggestions")
async def generate_suggestions(body: SuggestionRequest, request: Request):
    try:
        suggestion_graph = await run_in_threadpool(
            get_ai_model(request.app).suggest, project_id, body.story_context, body.limit
        )
        return [
            item.model_dump(mode="json")
            for item in suggestion_graph.suggestions
        ]
    except Exception as exc:
        _handle_error(exc)


@router.post(f"/projects/{project_id}/inspirations", status_code=status.HTTP_201_CREATED)
async def upload_inspiration(request: Request, file: UploadFile):
    """Upload a supported old-work file (PDF, image, TXT, or Markdown)."""
    suffix = Path(file.filename or "inspiration.txt").suffix or ".txt"
    temp_path = None
    try:
        contents = await file.read(20 * 1024 * 1024 + 1)
        if len(contents) > 20 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="Uploaded file exceeds the 20 MB limit")
        if not contents:
            raise HTTPException(status_code=422, detail="Uploaded file is empty")
        with NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
            temp_file.write(contents)
            temp_path = temp_file.name
        record = await run_in_threadpool(get_ai_model(request.app).add_inspiration, project_id, temp_path)
        return record.model_dump(mode="json", exclude={"embedding"})
    except HTTPException:
        raise
    except Exception as exc:
        _handle_error(exc)
    finally:
        if temp_path:
            Path(temp_path).unlink(missing_ok=True)


@router.post(f"/projects/{project_id}/inspirations/search")
async def search_inspirations(body: InspirationSearchRequest, request: Request):
    try:
        results = await run_in_threadpool(
            get_ai_model(request.app).search_inspiration, project_id, body.query, body.limit
        )
        return [
            {"record": item["record"].model_dump(mode="json", exclude={"embedding"}),
             "similarity": item["similarity"]}
            for item in results
        ]
    except Exception as exc:
        _handle_error(exc)


@router.get("/trends")
async def get_trending_topics():
    raise HTTPException(status_code=501, detail="Trending-topic data provider is not configured yet.")
