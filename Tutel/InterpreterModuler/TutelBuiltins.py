from copy import copy
from enum import Enum, auto
import numpy as np

from PySide6.QtCore import Qt, QPointF, Signal
from PySide6.QtGui import QColor


class Color(Enum):
    Blue = Qt.blue
    Green = Qt.green
    Cyan = Qt.cyan
    Gray = Qt.gray
    Red = Qt.red
    White = Qt.white
    Yellow = Qt.yellow
    Black = Qt.black


class Turtle:
    add_turtle: Signal = None
    set_color: Signal = None
    set_position: Signal = None
    set_orientation: Signal = None
    add_point: Signal = None
    id = 0

    def __init__(self):
        self.color = Color.Red.value
        self.position = Position(1, 1)
        self.__init_state = True
        self.orientation = Orientation(0)
        self.id = Turtle.id
        Turtle.id += 1
        if self.add_turtle is not None:
            self.add_turtle.emit(self.id, self.color, self.position, self.orientation)

    def setColor(self, color):
        self.color = color
        if self.set_color is not None:
            self.set_color.emit(self.id, self.color)

    def setPosition(self, x, y):
        self.position = Position(x, y)
        if self.set_position is not None:
            self.set_position.emit(self.id, self.position)

    def setOrientation(self, orientation):
        self.orientation = orientation
        if self.set_orientation is not None:
            self.set_orientation.emit(self.id, self.orientation)

    def turnLeft(self):
        self.setOrientation(self.orientation + 90)

    def turnRight(self):
        self.setOrientation(self.orientation - 90)

    @property
    def position(self):
        return self.__position

    @position.setter
    def position(self, pos):
        self.__position = pos

    @property
    def orientation(self):
        return self.__orientation

    @orientation.setter
    def orientation(self, deg):
        if deg is not None:
            self.__orientation = Orientation(int(np.mod(deg, 360)))

    def forward(self, a):
        if self.__init_state:
            if self.add_point is not None:
                self.add_point.emit(self.id, self.position)
            self.__init_state = False
        self.position.setX(self.position.x() + np.sin((self.orientation/360)*2*np.pi) * a)
        self.position.setY(self.position.y() + np.cos((self.orientation/360)*2*np.pi) * a)
        # self._positions.append(copy(self.position))
        if self.add_point is not None:
            self.add_point.emit(self.id, self.position)

    @classmethod
    def set_up(cls, add_turtle, set_color, set_position, set_orientation, add_point):
        cls.add_turtle = add_turtle
        cls.set_color = set_color
        cls.set_position = set_position
        cls.set_orientation = set_orientation
        cls.add_point = add_point


class Position:
    def __new__(cls, x, y):
        return QPointF(x, y)


class Orientation(int):
    pass
