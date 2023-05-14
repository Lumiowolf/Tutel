import json
import sys
from enum import Enum

from tutel import GuiModule
from tutel.GuiModule.GuiInterface import GuiInterface
from tutel.InterpreterModule.Turtle.Color import Color
from tutel.InterpreterModule.JsonSerializable import JsonSerializable
from tutel.InterpreterModule.Turtle.Orientation import Orientation
from tutel.InterpreterModule.Turtle.Position import Position
from tutel.InterpreterModule.Turtle.Turtle import Turtle


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


# def get_json(*objects):
#     return json.dumps(objects)
#     # dict_ = {}
#     # for object_ in objects:
#     #     dict_.update(object_.dict())
#     # return json.dumps(dict_)


def create_request(method: str, id: int, body):
    return json.dumps({"method": method, "id": id, "body": body},
                      default=lambda o: o.to_json() if isinstance(o, JsonSerializable) else o)


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
