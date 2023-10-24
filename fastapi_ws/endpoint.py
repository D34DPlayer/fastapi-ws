import json
import urllib.parse
from typing import Optional

from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import ValidationError

from .asyncapi.templates import asyncapi_html
from .asyncapi.types import AsyncApi
from .manager import WebsocketManager
from .ws_payloads import Payload, create_error


class WebsocketEndpoint(WebsocketManager):
    path: str
    asyncapi_path: str
    asyncapi_schema: Optional[AsyncApi]

    def __init__(self, app: FastAPI, path: str):
        super().__init__()

        self.path = path
        app.add_websocket_route(self.path, self.websocket_endpoint)
        app.add_route(self.path, self.docs_endpoint)
        self.asyncapi_path = urllib.parse.urljoin(path + "/", "./asyncapi.json")
        app.add_route(self.asyncapi_path, self.asyncapi_endpoint)

        self.asyncapi_schema = None

    def generate_asyncapi(self):
        schema = {
            "asyncapi": "2.6.0",
            "info": {
                "title": "Docs WS",
                "version": "0.0.0",
                "description": "DESC",
            },
            "channels": {
                "hello": {
                    "publish": {
                        "message": {
                            "messageId": "sayHello",
                            "payload": {"type": "string", "pattern": "^hello .+$"},
                        }
                    }
                }
            },
        }
        self.asyncapi_schema = schema

    @property
    def asyncapi(self):
        if not self.asyncapi_schema:
            self.generate_asyncapi()
        return self.asyncapi_schema

    async def websocket_endpoint(self, ws: WebSocket):
        await self.connect(ws)
        try:
            while True:
                data = await ws.receive_text()
                try:
                    parsed_data = json.loads(data)
                    payload = Payload(**parsed_data)
                except (ValidationError, TypeError):
                    error_payload = create_error("Invalid payload").model_dump_json()
                    await ws.send_text(error_payload)
                    continue
                except json.JSONDecodeError:
                    error_payload = create_error("Invalid JSON").model_dump_json()
                    await ws.send_text(error_payload)
                    continue

                if payload.type == "subscribe":
                    self.subscribe(payload.channel, ws)
                elif payload.type == "unsubscribe":
                    try:
                        self.unsubscribe(payload.channel, ws)
                    except KeyError:
                        error_payload = create_error(
                            "Not subscribed to " + payload.channel
                        ).model_dump_json()
                        await ws.send_text(error_payload)
                elif payload.type == "publish":
                    error_payload = create_error(
                        "Publish not yet implemented"
                    ).model_dump_json()
                    await ws.send_text(error_payload)

        except WebSocketDisconnect:
            await self.disconnect(ws)

    def asyncapi_endpoint(self, _: Request):
        return JSONResponse(self.asyncapi)

    def docs_endpoint(self, _: Request):
        return HTMLResponse(
            asyncapi_html("Websocket documentation", self.asyncapi_path),
        )
