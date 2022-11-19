from tutel.GuiModule.GuiInterface import GuiInterface
from tutel.InterpreterModule.Turtle.Color import Color
from tutel.InterpreterModule.Turtle.Position import Position


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

    def set_orientation(self, turtle_id: int, orientation: int) -> bool:
        self._message(f"Set orientation of [{turtle_id}] to [{orientation}]")
        return True

    def add_turtle(self, turtle_id: int, color: Color, position: Position, orientation: int) -> bool:
        self._message(f"Add [{turtle_id}]: [{color}]; [{position}]; [{orientation}]")
        return True
