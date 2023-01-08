from io import StringIO
from typing import Literal, NamedTuple

import tutel
from tutel import GuiModule
from tutel.ErrorHandlerModule.ErrorType import LexerException, ParserException, InterpreterException
from tutel.InterpreterModule.Interpreter import Interpreter
from tutel.LexerModule.Lexer import Lexer
from tutel.ParserModule.Parser import Parser


class TutelOptions(NamedTuple):
    gui: Literal["vscode", "nock"] = "mock"
    gui_out_path: str = ""
    verbose: bool = False


class Tutel:
    def __init__(self, code: str, options: TutelOptions = TutelOptions()):
        self.code = code
        self.options = options
        self.parser = Parser()
        self.program = None
        self.interpreter = Interpreter()
        self._prepare_to_run()

    def run(self):
        if self.options.gui_out_path:
            with open(self.options.gui_out_path, "w"):
                pass
        try:
            self.interpreter.execute(self.program, "main")
        except InterpreterException:
            exit(-4)

    def _prepare_to_run(self):
        try:
            lexer = Lexer(StringIO(self.code))
            self.program = self.parser.parse(lexer)
        except LexerException:
            exit(-2)
        except ParserException:
            exit(-3)
        if self.options.gui == "vscode":
            from tutel.GuiModule.GuiVsCode import GuiVsCode
            GuiModule.GUI = GuiVsCode()
        if self.options.verbose is True:
            tutel.VERBOSE = True
        if self.options.gui_out_path:
            GuiModule.GUI_OUT = self.options.gui_out_path
