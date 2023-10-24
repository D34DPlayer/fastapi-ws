from fastapi import FastAPI

from fastapi_ws.endpoint import WebsocketEndpoint

app = FastAPI(title="fastapi-ws")

endpoint = WebsocketEndpoint(app, "/ws")
