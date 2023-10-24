from enum import Enum
from typing import Any, Union, Literal

from pydantic import BaseModel


class PayloadType(str, Enum):
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    PUBLISH = "publish"
    ERROR = "error"


class PayloadSubscribe(BaseModel):
    type: Literal[PayloadType.SUBSCRIBE]
    channel: str


class PayloadUnsubscribe(BaseModel):
    type: Literal[PayloadType.UNSUBSCRIBE]
    channel: str


class PayloadPublish(BaseModel):
    type: Literal[PayloadType.PUBLISH]
    channel: str
    payload: Any


class PayloadError(BaseModel):
    type: Literal[PayloadType.ERROR]
    message: str


PayloadUnion = Union[PayloadSubscribe, PayloadUnsubscribe, PayloadPublish, PayloadError]


def Payload(type: str, **kwargs) -> PayloadUnion:
    if type == PayloadType.SUBSCRIBE:
        return PayloadSubscribe(type=type, **kwargs)
    elif type == PayloadType.UNSUBSCRIBE:
        return PayloadUnsubscribe(type=type, **kwargs)
    elif type == PayloadType.PUBLISH:
        return PayloadPublish(type=type, **kwargs)
    elif type == PayloadType.ERROR:
        return PayloadError(type=type, **kwargs)
    else:
        raise TypeError("Invalid payload type")


def create_error(message: str) -> PayloadError:
    return PayloadError(type=PayloadType.ERROR, message=message)
