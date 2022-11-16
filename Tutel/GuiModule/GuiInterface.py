from Tutel.InterpreterModuler.Turtle.Color import Color
from Tutel.InterpreterModuler.Turtle.Position import Position


class GuiInterface:
    @staticmethod
    def set_color(turtle_id: int, color: Color) -> bool:
        return True

    @staticmethod
    def set_position(turtle_id: int, position: Position) -> bool:
        return True

    @staticmethod
    def set_orientation(turtle_id: int, orientation: int) -> bool:
        return True

    @staticmethod
    def add_turtle(turtle_id: int, color: Color, position: Position, orientation: int) -> bool:
        return True
