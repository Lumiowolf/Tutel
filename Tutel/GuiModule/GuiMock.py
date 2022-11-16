from Tutel.GuiModule.GuiInterface import GuiInterface
from Tutel.InterpreterModuler.Turtle.Color import Color
from Tutel.InterpreterModuler.Turtle.Position import Position


class GuiMock(GuiInterface):
    @staticmethod
    def set_color(turtle_id: int, color: Color) -> bool:
        print(f"Set color of [{turtle_id}] to [{color}]")
        return True

    @staticmethod
    def set_position(turtle_id: int, position: Position) -> bool:
        print(f"Set position of [{turtle_id}] to [{position}]")
        return True

    @staticmethod
    def set_orientation(turtle_id: int, orientation: int) -> bool:
        print(f"Set orientation of [{turtle_id}] to [{orientation}]")
        return True

    @staticmethod
    def add_turtle(turtle_id: int, color: Color, position: Position, orientation: int) -> bool:
        print(f"Add [{turtle_id}]: [{color}]; [{position}]; [{orientation}]")
        return True
