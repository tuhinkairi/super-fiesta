import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from pymongo import AsyncMongoClient


# Resolve the repository-root .env so startup works from any working directory.
ROOT_ENV = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(ROOT_ENV)

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

    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        try:
            response = await self.client.admin.command("ping")
            if response.get("ok") != 1:
                raise ConnectionError("MongoDB ping did not succeed")
            db = self.client.get_database(self.database_name)

            print("database connected and collections checked")
            app.state.db = db
            app.state.mongo_client = self.client
            yield
        finally:
            await self.client.close()
