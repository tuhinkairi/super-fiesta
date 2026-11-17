from fastapi import FastAPI
from src.setup.db import Database
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start shared backend resources and release them on shutdown."""
    db_lifespan = Database().lifespan
    async with db_lifespan(app):
        app.state.ai_models = None
        try:
            yield
        finally:
            if app.state.ai_models is not None:
                app.state.ai_models.close()


class Server:
    def __init__(self) -> None:
        self.app = FastAPI(lifespan=lifespan)

    def create_app(self) -> FastAPI:
        return self.app

server = Server() 
app = server.create_app()

