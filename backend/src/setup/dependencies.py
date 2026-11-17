from fastapi import Request


def get_db(request: Request):
    """Return the database created by the application lifespan."""
    return request.app.state.db
