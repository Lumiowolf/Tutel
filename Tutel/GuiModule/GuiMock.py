from Tutel.GuiModule.GuiInterface import GuiInterface
from Tutel.InterpreterModuler.Turtle.Color import Color
from Tutel.InterpreterModuler.Turtle.Position import Position


class GuiMock(GuiInterface):
    silent = True

    @classmethod
    def __init__(cls, silent: bool = True) -> None:
        cls.silent = silent

    @classmethod
    def _message(cls, msg: str):
        if not cls.silent:
            print(msg)

    @classmethod
    def set_color(cls, turtle_id: int, color: Color) -> bool:
        cls._message(f"Set color of [{turtle_id}] to [{color}]")
        return True

    @classmethod
    def set_position(cls, turtle_id: int, position: Position) -> bool:
        cls._message(f"Set position of [{turtle_id}] to [{position}]")
        return True

    @classmethod
    def set_orientation(cls, turtle_id: int, orientation: int) -> bool:
        cls._message(f"Set orientation of [{turtle_id}] to [{orientation}]")
        return True

    @classmethod
    def add_turtle(cls, turtle_id: int, color: Color, position: Position, orientation: int) -> bool:
        cls._message(f"Add [{turtle_id}]: [{color}]; [{position}]; [{orientation}]")
        return True
