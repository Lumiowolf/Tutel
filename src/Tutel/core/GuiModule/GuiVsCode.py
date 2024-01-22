import json
import sys
from enum import Enum

from Tutel.core import GuiModule
from Tutel.core.GuiModule.GuiInterface import GuiInterface
from Tutel.core.InterpreterModule.Turtle.Color import Color
from Tutel.common.JsonSerializable import JsonSerializable
from Tutel.core.InterpreterModule.Turtle.Orientation import Orientation
from Tutel.core.InterpreterModule.Turtle.Position import Position
from Tutel.core.InterpreterModule.Turtle.Turtle import Turtle


class Methods(Enum):
    ADD = "ADD"
    COLOR = "COLOR"
    POSITION = "POSITION"
    ORIENTATION = "ORIENTATION"
    GO = "GO"


def _message(msg: str):
    if GuiModule.GUI_OUT:
        with open(GuiModule.GUI_OUT, "a") as f:
            f.write(msg)
    else:
        sys.stdout.write(msg)


def create_request(method: str, id: int = None, body=None):
    raw = {"method": method}
    if id is not None:
        raw["id"] = id
    if body is not None:
        raw["body"] = body
    return json.dumps(raw, default=lambda o: o.to_json() if isinstance(o, JsonSerializable) else o) + "\n"


class GuiVsCode(GuiInterface):
    def add_turtle(self, turtle: Turtle) -> bool:
        request = create_request(
            method="ADD", id=turtle.id, body=turtle
        )
        _message(request)
        return True

    def set_color(self, turtle_id: int, color: Color) -> bool:
        request = create_request(method="COLOR", id=turtle_id, body={"color": color})
        _message(request)
        return True

    def set_position(self, turtle_id: int, position: Position) -> bool:
        request = create_request(method="POSITION", id=turtle_id, body={"position": position})
        _message(request)
        return True

    def set_orientation(self, turtle_id: int, orientation: Orientation) -> bool:
        request = create_request(method="ORIENTATION", id=turtle_id, body={"orientation": orientation})
        _message(request)
        return True

    def go_forward(self, turtle_id: int, position: Position) -> bool:
        request = create_request(method="GO", id=turtle_id, body={"position": position})
        _message(request)
        return True
