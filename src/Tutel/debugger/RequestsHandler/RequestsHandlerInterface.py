from queue import Queue

from Tutel.debugger.RequestsHandler.DataStructures import DebuggerRequest, DebuggerResponse, DebuggerEvent


class RequestsHandlerInterface:
    running = True
    request_queue: Queue[tuple[DebuggerRequest, DebuggerResponse]] = None
    _instance: "RequestsHandlerInterface" = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(RequestsHandlerInterface, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def start(self, request_queue: Queue[tuple[DebuggerRequest, DebuggerResponse]]): ...
    def stop(self): ...
    def emit_event(self, event: DebuggerEvent): ...
    def join(self): ...