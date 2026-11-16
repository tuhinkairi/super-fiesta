from fastapi import FastAPI
from src.setup.db import Database
from src.controllers.users import router as users_router
from src.setup.dependencies import get_db


class Server:
    def __init__(self) -> None:
        self.db = Database()
        self.app = FastAPI(lifespan=self.db.lifespan)

    def create_app(self) -> FastAPI:
        return self.app

server = Server() 
app = server.create_app()
app.include_router(users_router)
