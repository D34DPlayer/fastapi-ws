from dataclasses import dataclass, field
from time import time
from typing import Set, List

from fastapi import WebSocket

from .event_listener import EventListener


@dataclass
class Connection:
    ws: WebSocket
    subscriptions: Set[str] = field(default_factory=set)
    created_at: float = field(default_factory=time)


class WebsocketManager(EventListener):
    connections: List[Connection]

    def __init__(self):
        super().__init__()
        self.connections = []

    def __index(self, ws: WebSocket) -> int:
        for i, con in enumerate(self.connections):
            if con.ws is ws:
                return i

    async def __connect(self, ws: WebSocket):
        await ws.accept()
        con = Connection(ws=ws, subscriptions=set())
        self.connections.append(con)
        await self.__emit("connect", con)

    async def __disconnect(self, ws: WebSocket):
        index = self.__index(ws)
        con = self.connections.pop(index)
        await self.__emit("disconnect", con)

    async def __broadcast(self, subscription: str, message: str) -> int:
        count = 0
        for connection in self.connections:
            if subscription in connection.subscriptions:
                await connection.ws.send_text(message)
                count += 1
        return count

    def __subscribe(self, subscription: str, ws: WebSocket):
        index = self.__index(ws)
        self.connections[index].subscriptions.add(subscription)

    def __unsubscribe(self, subscription: str, ws: WebSocket):
        index = self.__index(ws)
        self.connections[index].subscriptions.remove(subscription)
