import time
import builtins

from Tutel.core.InterpreterModule.Turtle.Color import Color
from Tutel.core.InterpreterModule.Turtle.Position import Position
from Tutel.core.InterpreterModule.Turtle.Turtle import Turtle
from Tutel.core.InterpreterModule.Value import Value


def print(*args) -> None:
    builtins.print(*args)


def input(*args) -> str:
    return builtins.input(*args)


def sleep(sec: int) -> None:
    time.sleep(sec)


def type(*args) -> Value[str]:
    return Value(builtins.type(*args).__name__)


def hex(number) -> Value[str]:
    return Value(builtins.hex(number))


def min(*args) -> Value:
    return Value(builtins.min(args))


def max(*args) -> Value:
    return Value(builtins.max(args))


def abs(number: Value) -> Value:
    return Value(builtins.abs(number))


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
