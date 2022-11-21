import math
import turtle
from turtle import Turtle, getscreen, colormode, screensize

from tutel.GuiModule.GuiInterface import GuiInterface
from tutel.InterpreterModule.TutelBuiltins import Color, Position


class GuiPythonBuiltinTurtle(GuiInterface):
    def __init__(self):
        self.turtles: dict[int, Turtle] = {}
        colormode(255)
        self.screen = getscreen()
        self.screen.bgcolor((0, 0, 0))
        self.central_point = (0.0, 0.0)
        print(self.screen.canvwidth)
        print(self.screen.canvheight)

    def add_turtle(self, turtle_id: int, color: Color, position: Position, orientation: int) -> bool:
        if turtle_id in self.turtles:
            return False
        try:
            new_turtle = Turtle()
            new_turtle.speed(0)
            new_turtle.hideturtle()
            new_turtle.penup()
            new_turtle.color(tuple(color))
            new_turtle.setpos(position.x, position.y)
            distance = turtle.distance(*self.central_point)
            if distance > self.screen.canvheight or distance > self.screen.canvwidth:
                screensize(math.ceil(distance), math.ceil(distance))
            new_turtle.setheading(orientation)
            new_turtle.pendown()
            new_turtle.showturtle()
        except:
            return False

        self.turtles[turtle_id] = new_turtle
        return True

    def go_forward(self, turtle_id: int, a: int) -> bool:
        if (turtle := self.turtles.get(turtle_id)) is None:
            return False
        try:
            turtle.forward(a)
            distance = turtle.distance(*self.central_point)
            if distance > self.screen.canvheight or distance > self.screen.canvwidth:
                screensize(math.ceil(distance), math.ceil(distance))
        except:
            return False

        return True

    def set_position(self, turtle_id: int, position: Position) -> bool:
        if (turtle := self.turtles.get(turtle_id)) is None:
            return False
        try:
            turtle.setpos(position.x, position.y)
            distance = turtle.distance(*self.central_point)
            if distance > self.screen.canvheight or distance > self.screen.canvwidth:
                screensize(math.ceil(distance), math.ceil(distance))
        except:
            return False

        return True

    def set_orientation(self, turtle_id: int, orientation: int) -> bool:
        if (turtle := self.turtles.get(turtle_id)) is None:
            return False
        try:
            turtle.setheading(orientation)
        except:
            return False

        return True

    def set_color(self, turtle_id: int, color: Color) -> bool:
        if (turtle := self.turtles.get(turtle_id)) is None:
            return False
        try:
            turtle.color(tuple(color))
        except:
            return False

        return True
