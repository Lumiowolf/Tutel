import argparse
import os
import sys

from tutel.ErrorHandlerModule.ErrorType import LexerException, ParserException, InterpreterException
from tutel.InterpreterModule.Interpreter import Interpreter, set_gui
from tutel.LexerModule.Lexer import Lexer
from tutel.ParserModule.Parser import Parser


def get_arg_parser():
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument(
        "filename",
        default=None,
        type=argparse.FileType('r'),
        help="Relative or absolute path to a script",
    )
    arg_parser.add_argument(
        "-v",
        "--verbose",
        default=False,
        action="store_true",
    )

    return arg_parser


def main(filename: str | None = None, flags: tuple[str] = None):
    if filename:
        sys.argv.append(filename)
    if flags:
        sys.argv += flags
    arg_parser = get_arg_parser()
    args = arg_parser.parse_args()

    args.filename = os.path.realpath(args.filename.name)

    with open(filename if filename is not None else args.filename, "r") as file:
        try:
            lexer = Lexer(file)
        except LexerException as e:
            exit(-2)
        parser = Parser()
        try:
            program = parser.parse(lexer)
        except ParserException as e:
            exit(-3)

    interpreter = Interpreter()
    from tutel.GuiModule.GuiMock import GuiMock

    set_gui(GuiMock(verbose=True))
    try:
        interpreter.execute(program, "main")
    except InterpreterException as e:
        exit(-4)
