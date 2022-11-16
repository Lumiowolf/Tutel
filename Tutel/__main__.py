import atexit
import os
import signal
import sys
from time import sleep

from Tutel.ErrorHandlerModule.ErrorHandler import ErrorHandler
from Tutel.ErrorHandlerModule.ErrorType import LexerException, ParserException, InterpreterException, \
    FileNotFoundException
from Tutel.InterpreterModuler.Interpreter import Interpreter
from Tutel.LexerModule.Lexer import Lexer
from Tutel.ParserModule.Parser import Parser


def main(file: str):
    error_handler = ErrorHandler()
    if not os.path.exists(file):
        error_handler.handle_error(
            FileNotFoundException(file_name=file)
        )
        exit(-1)
    with open(file, "r") as file:
        try:
            lexer = Lexer(file, error_handler)
        except LexerException as e:
            exit(-2)
        parser = Parser(error_handler)
        try:
            program = parser.parse(lexer)
        except ParserException as e:
            exit(-3)

    interpreter = Interpreter(error_handler)
    from Tutel.InterpreterModuler.Turtle.Turtle import Turtle
    from Tutel.GuiModule.GuiMock import GuiMock

    Turtle.set_gui(GuiMock())
    try:
        interpreter.execute(program, "main")
    except InterpreterException as e:
        exit(-4)


def _exit(*args):
    if _exit.alreadyExited:
        return
    _exit.alreadyExited = True
    print("Program terminated.")
    atexit._run_exitfuncs()
    for i in range(0, 3):
        sys.stdout.write(".")
        sys.stdout.flush()
        sleep(1)
    print()
    sys.exit(0)


_exit.alreadyExited = False

if __name__ == '__main__':
    signal.signal(signal.SIGINT, _exit)
    if len(sys.argv) >= 2:
        main(sys.argv[1])

if __debug__:
    signal.signal(signal.SIGINT, _exit)
    main("../../Examples/example_1.tut")
