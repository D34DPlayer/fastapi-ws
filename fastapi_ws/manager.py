from dataclasses import dataclass, field
from inspect import iscoroutinefunction
from time import time
from typing import Set, List, Callable, Any

from fastapi import WebSocket


@dataclass
class Connection:
    ws: WebSocket
    subscriptions: Set[str] = field(default_factory=set)
    created_at: float = field(default_factory=time)


class EventListener:
    callbacks: dict[str, list[Callable]]

    def __init__(self):
        self.callbacks = {}

    def on(self, event: str):
        """
        Decorator to register a callback for an event. Supports async.
        :param event: Event name
        :return: Decorator

        Example:
        ```
        @ws.on("connect")
        async def on_connect(payload):
            print("Client connected")
        ```
        """
        if event not in self.callbacks:
            self.callbacks[event] = []

        def decorator(func: Callable):
            self.callbacks[event].append(func)
            return func

        return decorator

    async def emit(self, event: str, payload: Any):
        """
        Emit an event to all listeners.
        :param event: Event name
        :param payload: Payload to send to listeners
        :return: Number of listeners called

        Example:
        ```
        await ws.emit("connect", {"message": "Client connected"})
        ```
        """
        callbacks = self.callbacks.get(event, [])
        for callback in callbacks:
            if iscoroutinefunction(callback):
                await callback(payload)
            callback(payload)

        return len(callbacks)


class WebsocketManager(EventListener):
    connections: List[Connection]

    def __init__(self):
        super().__init__()
        self.connections = []

    def index(self, ws: WebSocket) -> int:
        for i, con in enumerate(self.connections):
            if con.ws is ws:
                return i

    async def connect(self, ws: WebSocket):
        await ws.accept()
        con = Connection(ws=ws, subscriptions=set())
        self.connections.append(con)
        await self.emit("connect", con)

    async def disconnect(self, ws: WebSocket):
        index = self.index(ws)
        con = self.connections.pop(index)
        await self.emit("disconnect", con)

    async def broadcast(self, subscription: str, message: str) -> int:
        count = 0
        for connection in self.connections:
            if subscription in connection.subscriptions:
                await connection.ws.send_text(message)
                count += 1
        return count

    def subscribe(self, subscription: str, ws: WebSocket):
        index = self.index(ws)
        self.connections[index].subscriptions.add(subscription)

    def unsubscribe(self, subscription: str, ws: WebSocket):
        index = self.index(ws)
        self.connections[index].subscriptions.remove(subscription)
