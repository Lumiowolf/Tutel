import time
import builtins

from tutel.InterpreterModule.Turtle.Color import Color
from tutel.InterpreterModule.Turtle.Position import Position
from tutel.InterpreterModule.Turtle.Turtle import Turtle
from tutel.InterpreterModule.Value import Value


def print(*args) -> None:
    builtins.print(*args)


def input(prompt) -> str:
    return builtins.input(prompt)


def sleep(sec: int) -> None:
    time.sleep(sec)


def type(*args) -> Value[str]:
    return Value(builtins.type(*args).__name__)


def hex(number) -> Value[str]:
    return Value(builtins.hex(number))


def range(*args) -> Value[range]:
    return Value(builtins.range(*args))


def len(obj) -> Value[int]:
    return Value(builtins.len(obj))


def pow(exp: int, mod: int) -> Value[int]:
    return Value(builtins.pow(exp, mod))


def str(*args):
    return builtins.str(*args)


def int(*args) -> Value[int]:
    return Value(builtins.int(*args))


Turtle = Turtle.turtle_init
Color = Color
Position = Position
