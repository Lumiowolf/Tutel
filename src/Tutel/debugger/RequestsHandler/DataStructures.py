import json

from Tutel.common.JsonSerializable import JsonSerializable
from Tutel.debugger.RequestsHandler.Commands import Command


class DebuggerRequest:
    command: Command = None
    args: tuple[int, str, ...] = ()

    def __init__(self, command: Command = None, args: tuple[int, ...] | tuple[str, ...] | tuple[int, str, ...] = ()):
        self.command = command
        self.args = args

    def __repr__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        return type(self) == type(other) and self.command == other.command and self.args == other.args

class DebuggerResponse:
    response: str = None
    body: dict = None

    def __init__(self, response: str = None, body: dict = None):
        self.response = response
        self.body = body

    def serialize(self) -> str:
        raw = {"response": self.response, "body": self.body}
        return json.dumps(raw, default=lambda o: o.to_json() if isinstance(o, JsonSerializable) else o)

    def __repr__(self):
        return str(self.__dict__)

class DebuggerEvent:
    event: str = None
    description: str = None

    def __init__(self, event: str = None, description: str = None):
        self.event = event
        self.description = description

    def serialize(self) -> str:
        raw = {"event": self.event, "description": self.description}
        return json.dumps(raw, default=lambda o: o.to_json() if isinstance(o, JsonSerializable) else o)

    def __repr__(self):
        return str(self.__dict__)
