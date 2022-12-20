import argparse
import os
import sys
from io import StringIO

import tutel
from tutel.ErrorHandlerModule.ErrorType import LexerException, ParserException, InterpreterException
from tutel.InterpreterModule.Interpreter import Interpreter, set_gui, set_verbose
from tutel.LexerModule.Lexer import Lexer
from tutel.ParserModule.Parser import Parser


def get_arg_parser():
    arg_parser = argparse.ArgumentParser()

    group = arg_parser.add_mutually_exclusive_group(required=False)

    group.add_argument(
        "-f",
        "--filename",
        default=None,
        type=argparse.FileType('r'),
        help="Relative or absolute path to a script",
    )
    group.add_argument(
        "-c",
        "--code",
        default=None,
        type=str,
        help="Code to execute as a string",
    )

    arg_parser.add_argument(
        "-v",
        "--verbose",
        default=False,
        action="store_true",
    )
    arg_parser.add_argument(
        "--vscode",
        default=False,
        action="store_true",
    )
    arg_parser.add_argument(
        "--version",
        default=False,
        action="store_true",
    )

    return arg_parser


def main(filename: str | None = None, code: str | None = None, flags: tuple[str] = None):
    if filename and code:
        raise RuntimeError("You should give the filename or the code and not both of them.")
    if filename:
        sys.argv.append("-f")
        sys.argv.append(filename)
    if code:
        sys.argv.append("-c")
        sys.argv.append(code)
    if flags:
        sys.argv += flags
    arg_parser = get_arg_parser()
    args = arg_parser.parse_args()
    if args.version:
        print(f"Tutel {tutel.__version__}")
        exit(0)

    if hasattr(args, "filename") and args.filename:
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
    elif hasattr(args, "code") and args.code:
        try:
            lexer = Lexer(StringIO(args.code))
        except LexerException as e:
            exit(-2)
        parser = Parser()
        try:
            program = parser.parse(lexer)
        except ParserException as e:
            exit(-3)
    else:
        print("Nothing to execute")
        exit(0)

    interpreter = Interpreter()
    if args.vscode:
        from tutel.GuiModule.GuiVsCode import GuiVsCode

        set_gui(GuiVsCode())
    if args.verbose:
        set_verbose()
    try:
        interpreter.execute(program, "main")
    except InterpreterException as e:
        exit(-4)
