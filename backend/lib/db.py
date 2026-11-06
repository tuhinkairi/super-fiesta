from prisma import Prisma
from contextlib import asynccontextmanager
from fastapi import FastAPI

class PrismaConnection:
    """
    Class to manage Prisma database connection lifecycle with FastAPI.
    """
    def __init__(self):
        """
        Initialize PrismaConnection with a Prisma client instance.
        """
        self.db = Prisma()

    @asynccontextmanager
    async def lifespan(self, app:FastAPI):
        """
        Manage the lifespan of the database connection.

        Connects to the database when the FastAPI app starts and disconnects when it stops.

        Args:
            app (FastAPI): The FastAPI application instance.

        Yields:
            None
        """
        await self.db.connect()
        yield
        await self.db.disconnect()
        

prisma_connection = PrismaConnection()