from io import StringIO

import Tutel
from Tutel.core import GuiModule
from Tutel.common.ErrorType import LexerException, ParserException, InterpreterException
from Tutel.core.InterpreterModule.Interpreter import Interpreter
from Tutel.core.LexerModule.Lexer import Lexer
from Tutel.core.ParserModule.Parser import Parser
from Tutel.core.Runner.TutelOptions import TutelOptions


class TutelRunner:
    def __init__(self, code: str | None, options: TutelOptions = None):
        self.code = code
        self.options = options or TutelOptions()
        self.parser = Parser()
        self.program = None
        self.interpreter = Interpreter()

    def run(self):
        self._prepare_to_run()
        if self.options.gui_out_path:
            with open(self.options.gui_out_path, "w"):
                pass
        try:
            self.interpreter.execute(self.program, "main")
        except InterpreterException:
            exit(-4)

    def _prepare_to_run(self, debug=False):
        try:
            lexer = Lexer(StringIO(self.code))
            self.program = self.parser.parse(lexer)
        except LexerException as e:
            if debug:
                raise e
            exit(-2)
        except ParserException as e:
            if debug:
                raise e
            exit(-3)
        if self.options.gui == "vscode":
            from Tutel.core.GuiModule.GuiVsCode import GuiVsCode
            GuiModule.GUI = GuiVsCode()
        if self.options.verbose is True:
            Tutel.VERBOSE = True
        if self.options.gui_out_path:
            GuiModule.GUI_OUT = self.options.gui_out_path
