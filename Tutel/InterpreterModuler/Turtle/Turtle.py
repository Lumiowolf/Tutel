import numpy as np

from Tutel.GuiModule.GuiInterface import GuiInterface
from Tutel.InterpreterModuler.Turtle.Color import Color
from Tutel.InterpreterModuler.Turtle.Position import Position


class Turtle:
    id = 0
    gui: GuiInterface = GuiInterface()

    def __init__(self):
        self.__color = Color(255, 0, 0)
        self.__position = Position(1, 1)
        self.__orientation = 0
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
        if position is not None:
            if self.gui.set_position(self.id, position):
                self.__position = position

    def set_position(self, position: Position):
        self.position = position

    @property
    def orientation(self) -> int:
        return self.__orientation

    @orientation.setter
    def orientation(self, orientation: int):
        if orientation is not None:
            orientation = int(np.mod(orientation, 360))
            if self.gui.set_orientation(self.id, orientation):
                self.__orientation = orientation

    def set_orientation(self, orientation: int):
        self.orientation = orientation

    def turn_left(self):
        self.orientation = self.orientation + 90

    def turn_right(self):
        self.orientation = self.orientation - 90

    def forward(self, a):
        if self.__init_state:
            self.__init_state = False
        self.position = Position(
            x=self.position.x + np.sin((self.orientation / 360) * 2 * np.pi) * a,
            y=self.position.y + np.cos((self.orientation / 360) * 2 * np.pi) * a
        )
