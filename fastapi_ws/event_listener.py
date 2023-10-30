from inspect import iscoroutinefunction
from typing import Callable, Any


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

    async def __emit(self, event: str, payload: Any):
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
