"""
Definitions for Asyncapi 2.6.0
"""
from typing import TypedDict, Optional, Union, Literal

OneOf = Literal["oneOf"]


class Info(TypedDict):
    title: str
    version: str
    description: Optional[str]


class Message(TypedDict):
    name: Optional[str]
    title: Optional[str]
    summary: Optional[str]
    description: Optional[str]
    payload: None


class Operation(TypedDict):
    summary: Optional[str]
    description: Optional[str]
    message: Union[
        Message,
        dict[OneOf, list[Message]],
        None,
    ]


class Channel(TypedDict):
    description: Optional[str]
    subscribe: Optional[Operation]
    publish: Optional[Operation]


class Server(TypedDict):
    url: str
    protocol: str
    protocolVersion: Optional[str]
    description: Optional[str]


class AsyncApi(TypedDict):
    asyncapi: str
    info: Info
    # servers: dict[str, Server]
    channels: dict[str, Channel]
