import time

from Tutel.InterpreterModuler.Turtle.Color import Color
from Tutel.InterpreterModuler.Turtle.Position import Position
from Tutel.InterpreterModuler.Turtle.Turtle import Turtle


def print_(*args):
    print(*args)


def sleep_(sec: int):
    time.sleep(sec)


def type_(*args):
    return type(*args).__name__


def int_(*args):
    return int(*args)


def str_(*args):
    return str(*args)


def hex_(*args):
    return hex(*args)


def range_(*args):
    return range(*args)


def len_(*args):
    return len(*args)


GLOBAL_FUNCTIONS = {
    "print": print_,
    "sleep": sleep_,
    "type": type_,
    "int": int_,
    "str": str_,
    "hex": hex_,
    "range": range_,
    "len": len_,
    "Turtle": Turtle.turtle_init,
    "Color": Color,
    "Position": Position,
}
