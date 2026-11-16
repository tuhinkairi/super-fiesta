from src.setup.server import app

server_app = app
db = server_app.state._state["db"]