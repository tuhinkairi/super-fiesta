# Backend API

FastAPI exposes user CRUD and the AI workflows implemented by the top-level
`modules/` package. Run the app from `backend/` with `uvicorn main:app --reload`.
Set `DB_URI`, `DB_NAME`, and `GEMINI_API_KEY` in `backend/.env` before use.
`GEMINI_MODEL` can override the default `gemini-3.8-flash`; Gemini requests have a
45-second timeout and one attempt by default.

## AI routes

- `POST /ai/stories/analyze` — JSON `{ "project_id", "story_text", "chapter_number?" }`; extracts entities, events, relationships, timeline, and a pending graph.
- `POST /ai/stories/{project_id}/graph/approve` — approve the latest graph for the project.
- `POST /ai/stories/{project_id}/suggestions` — JSON `{ "story_context", "limit?" }`; requires an approved graph.
- `POST /ai/projects/{project_id}/inspirations` — multipart upload in a supported PDF, image, TXT, or Markdown format.
- `POST /ai/projects/{project_id}/inspirations/search` — JSON `{ "query", "limit?" }` for semantic retrieval.
- `GET /ai/trends` — reserved for a future trends data provider; currently returns `501`.

AI workflow state and the inspiration library are process-local in this initial
backend scaffold. Persisting projects and graph approval state across restarts
will need database-backed repositories.
