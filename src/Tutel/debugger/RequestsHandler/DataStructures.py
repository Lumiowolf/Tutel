import asyncio
import json
import threading
from enum import Enum, auto

from Tutel.common.JsonSerializable import JsonSerializable
from Tutel.debugger.RequestsHandler.Commands import Command


class DebuggerResponseType(JsonSerializable, Enum):
    FILE_SET = "file_set"
    STARTED = "started"
    RESUMED = "resumed"
    FRAME = "frame"
    STACK = "stack_trace"
    BPS = "breakpoints"
    BP_SET = "breakpoint_set"
    BP_CLEARED = "breakpoint_removed"
    ALL_BP_CLEARED = "all_breakpoints_removed"

    BAD_REQUEST = "bad_request"

    def to_json(self):
        return self.value


class DebuggerResponse:
    type: str = None
    body: dict = None

    def __init__(self, type: str = None, body: dict = None):
        self.type = type
        self.body = body

    def serialize(self) -> str:
        raw = {"type": self.type, "body": self.body}
        # print(raw)
        return json.dumps(raw, default=lambda o: o.to_json() if isinstance(o, JsonSerializable) else o)

    def __repr__(self):
        return str(self.__dict__)

class DebuggerRequestStatus(Enum):
    SUCCESS = auto()
    FAIL = auto()

class DebuggerRequest:
    def __init__(self, command: Command = None, args: tuple[int, ...] | tuple[str, ...] | tuple[int, str, ...] = ()):
        self.command: Command | None = command
        self.args: tuple[int, str, ...] = args
        self.status: DebuggerRequestStatus | None = None
        self.finished = threading.Event()

    def resolve(self):
        self.status = DebuggerRequestStatus.SUCCESS
        self.finished.set()
        # print("resolved")

    def reject(self):
        self.status = DebuggerRequestStatus.FAIL
        self.finished.set()
        # print("rejected")

    def __repr__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        return type(self) == type(other) and self.command == other.command and self.args == other.args

class DebuggerEvent:
    type: str = None
    description: str = None

    def __init__(self, type: str = None, description: str = None):
        self.type = type
        self.description = description

    def serialize(self) -> str:
        raw = {"type": self.type, "description": self.description}
        return json.dumps(raw, default=lambda o: o.to_json() if isinstance(o, JsonSerializable) else o)

    def __repr__(self):
        return str(self.__dict__)
