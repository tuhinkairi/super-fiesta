
from fastapi import FastAPI, HTTPException
from lib.db import prisma_connection
from typing import Literal, List, Optional, Callable, Any


class Server:
    """
    Manages FastAPI application configuration and lifecycle.
    """

    def __init__(self):
        self.app = FastAPI(
            lifespan=prisma_connection.lifespan
        )

    def run(
        self,
        host: str = "127.0.0.1",
        port: int = 8000,
        log_level: str = "info"
    ):
        import uvicorn

        uvicorn.run(
            self.app,
            host=host,
            port=port,
            log_level=log_level
        )

    def routeHandler(
        self,
        path: str,
        methods: List[Literal["GET", "POST", "PUT", "DELETE", "PATCH"]] = ["GET"],
        response_model: Optional[type] = None,
        callback: Optional[Callable[..., Any]] = None
    ):

        async def route():
            try:
                if callback is None:
                    return None

                return await callback()

            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=str(e)
                )

        # assigning the route 
        self.app.add_api_route(
            path,
            route,
            methods=methods,
            response_model=response_model
        )
