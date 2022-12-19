import math

from tutel.GuiModule.GuiInterface import GuiInterface
from tutel.GuiModule.GuiMock import GuiMock
from tutel.InterpreterModule.Turtle.Color import Color
from tutel.InterpreterModule.Turtle.Orientation import Orientation
from tutel.InterpreterModule.Turtle.Position import Position


class Turtle:
    id = 0
    gui: GuiInterface = GuiMock()

    def __init__(self):
        self.__color = Color(255, 0, 0)
        self.__position = Position(0, 0)
        self.__orientation = Orientation(0)
        self.__init_state = True
        self.id = Turtle.id
        Turtle.id += 1

    @classmethod
    def set_gui(cls, gui: GuiInterface):
        cls.gui = gui

    @classmethod
    def turtle_init(cls) -> "Turtle | None":
        turtle = cls()
        if cls.gui.add_turtle(
                turtle_id=turtle.id,
                color=turtle.color,
                position=turtle.position,
                orientation=turtle.orientation
        ):
            return turtle

    @property
    def color(self) -> Color:
        return self.__color

    @color.setter
    def color(self, color: Color):
        if color is not None:
            if self.gui.set_color(self.id, color):
                self.__color = color

    def set_color(self, color: Color):
        self.color = color

    @property
    def position(self) -> Position:
        return self.__position

    @position.setter
    def position(self, position: Position):
        self.__position = position

    def set_position(self, position: Position):
        if position is not None:
            if self.gui.set_position(self.id, position):
                self.position = position

    @property
    def orientation(self) -> Orientation:
        return self.__orientation

    @orientation.setter
    def orientation(self, orientation: Orientation):
        if orientation is not None:
            orientation = Orientation(int(orientation.angle % 360))
            if self.gui.set_orientation(self.id, orientation):
                self.__orientation = orientation

    def set_orientation(self, orientation: int):
        self.orientation = Orientation(orientation)

    def turn_left(self):
        self.set_orientation(self.orientation.angle + 90)

    def turn_right(self):
        self.set_orientation(self.orientation.angle - 90)

    def forward(self, a: int):
        if self.__init_state:
            self.__init_state = False
        if a is not None:
            new_position = Position(
                x=self.position.x + math.sin((self.orientation.angle / 360) * 2 * math.pi) * a,
                y=self.position.y + math.cos((self.orientation.angle / 360) * 2 * math.pi) * a
            )
            if self.gui.go_forward(self.id, new_position):
                self.position = new_position
