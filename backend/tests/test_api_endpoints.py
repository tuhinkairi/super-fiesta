"""Endpoint tests that isolate the API from live MongoDB and Gemini services."""

from __future__ import annotations

from contextlib import asynccontextmanager
from copy import deepcopy
import json
import logging
import os
from pathlib import Path
import sys
from uuid import uuid4

import pytest
from dotenv import dotenv_values
from fastapi.testclient import TestClient

# The app is normally launched with ``backend/`` as the working directory.
# Add that directory explicitly so this test also works when pytest is started
# from the repository root (as IDE test runners commonly do).
BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

import main

LOG_DIR = BACKEND_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
RESPONSE_LOG = LOG_DIR / "api_test_responses.jsonl"
response_logger = logging.getLogger("api_endpoint_test_responses")
response_logger.setLevel(logging.INFO)
if not response_logger.handlers:
    file_handler = logging.FileHandler(RESPONSE_LOG, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(message)s"))
    response_logger.addHandler(file_handler)


class ResponseLoggingTestClient(TestClient):
    """Persist each endpoint response as a JSON Lines record."""

    def send(self, request, **kwargs):
        response = super().send(request, **kwargs)
        response.read()
        response_logger.info(json.dumps({
            "test": os.getenv("PYTEST_CURRENT_TEST", "direct invocation"),
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "response": response.text,
        }, ensure_ascii=False))
        return response


class Payload:
    def __init__(self, data: dict):
        self.data = data

    def model_dump(self, **_kwargs):
        return deepcopy(self.data)


class FakeAIModel:
    def __init__(self):
        self.analyzed_projects: list[str] = []
        self.approved_projects: list[str] = []
        self.suggested_projects: list[str] = []
        self.uploaded_projects: list[str] = []
        self.searched_projects: list[str] = []

    def analyze_story(self, project_id, story_text, chapter_number=None):
        self.analyzed_projects.append(project_id)
        return Payload({
            "project_id": project_id,
            "story_text": story_text,
            "chapter_number": chapter_number,
            "processing_status": "completed",
        })

    def approve_graph(self, project_id):
        self.approved_projects.append(project_id)
        return Payload({"project_id": project_id, "approval_status": "approved"})

    def suggest(self, project_id, story_context, limit):
        self.suggested_projects.append(project_id)
        return [Payload({"title": "A hidden clue", "context": story_context})][:limit]

    def add_inspiration(self, project_id, file_path):
        assert Path(file_path).is_file()
        self.uploaded_projects.append(project_id)
        return Payload({"id": "inspiration-test", "file_name": "old-work.txt"})

    def search_inspiration(self, project_id, query, limit):
        self.searched_projects.append(project_id)
        return [{
            "record": Payload({"id": "inspiration-test", "summary": query}),
            "similarity": 0.9,
        }][:limit]

    def close(self):
        pass


class FakeCursor:
    def __init__(self, records: list[dict]):
        self.records = records

    async def to_list(self, length=None):
        records = self.records if length is None else self.records[:length]
        return deepcopy(records)


class FakeCollection:
    def __init__(self):
        self.records: dict[object, dict] = {}

    async def insert_one(self, record):
        from bson import ObjectId

        record = deepcopy(record)
        record["_id"] = ObjectId()
        self.records[record["_id"]] = record
        return type("InsertResult", (), {"inserted_id": record["_id"]})()

    def find(self, _query, _projection=None):
        return FakeCursor(list(self.records.values()))

    async def find_one(self, query, _projection=None):
        record = self.records.get(query.get("_id"))
        return deepcopy(record) if record else None

    async def update_one(self, query, update):
        record = self.records.get(query.get("_id"))
        if record:
            record.update(deepcopy(update.get("$set", {})))

    async def delete_one(self, query):
        deleted = self.records.pop(query.get("_id"), None)
        return type("DeleteResult", (), {"deleted_count": int(deleted is not None)})()


class FakeDatabase:
    def __init__(self):
        self.collections = {"users": FakeCollection()}

    def __getitem__(self, collection_name):
        return self.collections[collection_name]


@pytest.fixture
def project_id() -> str:
    # Keep the project identifier in local configuration; tests supply it to
    # the API from .env and never prompt the caller for it.
    env_path = BACKEND_ROOT.parent / ".env"
    project_id = dotenv_values(env_path).get("PROJECT_ID") if env_path.exists() else None
    if not project_id:
        pytest.skip("Set PROJECT_ID in the repository-root .env to exercise project-scoped routes")
    return project_id.strip().rstrip("\\")


@pytest.fixture
def client(monkeypatch):
    fake_ai = FakeAIModel()
    fake_db = FakeDatabase()

    @asynccontextmanager
    async def test_lifespan(app):
        app.state.ai_models = fake_ai
        app.state.db = fake_db
        yield
        fake_ai.close()

    monkeypatch.setattr(main.app.router, "lifespan_context", test_lifespan)
    with ResponseLoggingTestClient(main.app) as test_client:
        yield test_client, fake_ai


def test_openapi_is_available(client):
    test_client, _ = client
    response = test_client.get("/openapi.json")
    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/users" in paths
    assert "/ai/stories/analyze" in paths


def test_user_crud_endpoints(client):
    test_client, _ = client
    created = test_client.post("/users", json={
        "name": "Endpoint Test",
        "email": f"endpoint-{uuid4().hex}@example.com",
        "hash_pass": "temporary-test-password",
        "role": "User",
    })
    assert created.status_code == 201
    user_id = created.json()["_id"]
    assert "hash_pass" not in created.json()

    listed = test_client.get("/users")
    assert listed.status_code == 200
    assert any(user["_id"] == user_id for user in listed.json())

    fetched = test_client.get(f"/users/{user_id}")
    assert fetched.status_code == 200
    assert fetched.json()["_id"] == user_id

    updated = test_client.patch(f"/users/{user_id}", json={"name": "Updated Endpoint Test"})
    assert updated.status_code == 200
    assert updated.json()["name"] == "Updated Endpoint Test"

    deleted = test_client.delete(f"/users/{user_id}")
    assert deleted.status_code == 204
    assert test_client.get(f"/users/{user_id}").status_code == 404


def test_ai_endpoints_with_env_project_id(client, project_id):
    test_client, fake_ai = client
    story_text = "Mira finds a key in an observatory and shows it to Arun."

    analyzed = test_client.post("/ai/stories/analyze", json={
        "project_id": project_id,
        "story_text": story_text,
        "chapter_number": 1,
    })
    assert analyzed.status_code == 200
    assert analyzed.json()["project_id"] == project_id
    assert fake_ai.analyzed_projects == [project_id]

    # PROJECT_ID is a Google resource name containing '/', so these verify the
    # routes preserve and accept its whole value as a single project identifier.
    approved = test_client.post(f"/ai/stories/{project_id}/graph/approve")
    assert approved.status_code == 200
    assert fake_ai.approved_projects == [project_id]

    suggestions = test_client.post(
        f"/ai/stories/{project_id}/suggestions",
        json={"story_context": story_text, "limit": 1},
    )
    assert suggestions.status_code == 200
    assert suggestions.json()[0]["title"] == "A hidden clue"
    assert fake_ai.suggested_projects == [project_id]

    uploaded = test_client.post(
        f"/ai/projects/{project_id}/inspirations",
        files={"file": ("old-work.txt", b"A short piece of old work.", "text/plain")},
    )
    assert uploaded.status_code == 201
    assert uploaded.json()["id"] == "inspiration-test"
    assert fake_ai.uploaded_projects == [project_id]

    searched = test_client.post(
        f"/ai/projects/{project_id}/inspirations/search",
        json={"query": "old work", "limit": 1},
    )
    assert searched.status_code == 200
    assert searched.json()[0]["similarity"] == 0.9
    assert fake_ai.searched_projects == [project_id]

    trends = test_client.get("/ai/trends")
    assert trends.status_code == 501
    assert "provider is not configured" in trends.json()["detail"]


if __name__ == "__main__":
    # Running this file directly should execute the tests and show a report,
    # instead of importing the test definitions and exiting silently.
    exit_code = pytest.main([__file__, "-v", "-s", "-p", "no:cacheprovider"])
    print(f"\nAPI response logs saved to: {RESPONSE_LOG}")
    raise SystemExit(exit_code)
