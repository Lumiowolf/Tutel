import math

from Tutel.core import GuiModule
from Tutel.core.GuiModule import GuiInterface
from Tutel.core.InterpreterModule.Turtle.Color import Color
from Tutel.common.JsonSerializable import JsonSerializable
from Tutel.core.InterpreterModule.Turtle.Orientation import Orientation
from Tutel.core.InterpreterModule.Turtle.Position import Position


class Turtle(JsonSerializable):
    default_id = 0
    id = 0

    def __init__(self):
        self.__color = Color(255, 0, 0)
        self.__position = Position(0, 0)
        self.__orientation = Orientation(0)
        self.__init_state = True
        self.id = Turtle.id
        Turtle.id += 1

    @classmethod
    def turtle_init(cls) -> "Turtle | None":
        turtle = cls()
        if GuiModule.GUI.add_turtle(
                turtle=turtle,
        ) or type(GuiModule.GUI) == GuiInterface:
            return turtle

    @property
    def color(self) -> Color:
        return self.__color

    @color.setter
    def color(self, color: Color):
        if color is not None:
            if GuiModule.GUI.set_color(self.id, color) or type(GuiModule.GUI) == GuiInterface:
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
            if GuiModule.GUI.set_position(self.id, position) or type(GuiModule.GUI) == GuiInterface:
                self.position = position

    @property
    def orientation(self) -> Orientation:
        return self.__orientation

    @orientation.setter
    def orientation(self, orientation: Orientation):
        if orientation is not None:
            orientation = Orientation(int(orientation % 360))
            if GuiModule.GUI.set_orientation(self.id, orientation) or type(GuiModule.GUI) == GuiInterface:
                self.__orientation = orientation

    def set_orientation(self, orientation: int):
        self.orientation = Orientation(orientation)

    def turn_left(self):
        self.set_orientation(self.orientation + 90)

    def turn_right(self):
        self.set_orientation(self.orientation - 90)

    def forward(self, a: int):
        if self.__init_state:
            self.__init_state = False
        if a is not None:
            new_position = Position(
                x=self.position.x + math.sin((self.orientation / 360) * 2 * math.pi) * a,
                y=self.position.y + math.cos((self.orientation / 360) * 2 * math.pi) * a
            )
            if GuiModule.GUI.go_forward(self.id, new_position) or type(GuiModule.GUI) == GuiInterface:
                self.position = new_position

    def to_json(self):
        return {
            "color": self.color,
            "position": self.position,
            "orientation": self.orientation,
        }

    def __repr__(self):
        return "{" + f'"id": {self.id}, ' \
                     f'"color": {self.color}, ' \
                     f'"position": {self.position}, ' \
                     f'"orientation": {self.orientation}' + "}"
