import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from pymongo import AsyncMongoClient


# Resolve the backend .env from this file so startup works regardless of the
# directory from which Uvicorn is launched.
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

# Collections required by the application. MongoDB creates collections on
# first write, but creating them here makes the database ready at startup.
REQUIRED_COLLECTIONS = ("users",)


class Database:
    def __init__(self) -> None:
        connection_uri = os.getenv("DB_URI")
        database_name = os.getenv("DB_NAME")

        if not connection_uri or not database_name:
            raise RuntimeError("DB_URI and DB_NAME must be set in the environment")

        self.database_name = database_name
        self.client = AsyncMongoClient(connection_uri)

    async def ensure_collections(self, db) -> None:
        """Create required collections that do not exist yet."""
        existing_collections = set(await db.list_collection_names())
        for collection_name in REQUIRED_COLLECTIONS:
            if collection_name not in existing_collections:
                await db.create_collection(collection_name)

    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        try:
            # AsyncMongoClient connects lazily; ping verifies the server is
            # reachable before the application starts serving requests.
            response = await self.client.admin.command("ping")
            if response.get("ok") != 1:
                raise ConnectionError("MongoDB ping did not succeed")
            db = self.client.get_database(self.database_name)
            await self.ensure_collections(db)

            print("database connected and collections checked")
            app.state.db = db
            app.state.mongo_client = self.client
            yield
        finally:
            await self.client.close()
