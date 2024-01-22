from Tutel.core.GuiModule.GuiInterface import GuiInterface
from Tutel.core.InterpreterModule.Turtle.Color import Color
from Tutel.core.InterpreterModule.Turtle.Orientation import Orientation
from Tutel.core.InterpreterModule.Turtle.Position import Position
from Tutel.core.InterpreterModule.Turtle.Turtle import Turtle


class GuiMock(GuiInterface):
    def __init__(self, verbose: bool = False) -> None:
        self.verbose = verbose

    def _message(self, msg: str):
        if self.verbose:
            print(msg)

    def set_color(self, turtle_id: int, color: Color) -> bool:
        self._message(f"Set color of [{turtle_id}] to [{color}]")
        return True

    def set_position(self, turtle_id: int, position: Position) -> bool:
        self._message(f"Set position of [{turtle_id}] to [{position}]")
        return True

    def set_orientation(self, turtle_id: int, orientation: Orientation) -> bool:
        self._message(f"Set orientation of [{turtle_id}] to [{orientation}]")
        return True

    def add_turtle(self, turtle: Turtle) -> bool:
        self._message(f"Add [{turtle.id}]: [{turtle.color}]; [{turtle.position}]; [{turtle.orientation}]")
        return True

    def go_forward(self, turtle_id: int, position: Position) -> bool:
        self._message(f"Go forward [{turtle_id}] by [{position}]")
        return True

