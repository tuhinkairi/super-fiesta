from src.setup.server import app
import uvicorn
from src.controllers.users import router as users_router

app.include_router(users_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000)
