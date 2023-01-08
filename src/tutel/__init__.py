__version__ = "2.0.2"

from .InterpreterModule.Interpreter import Interpreter as TutelInterpreter
from .LexerModule.Lexer import Lexer as TutelLexer
from .ParserModule.Parser import Parser as TutelParser
from .Tutel import Tutel as Tutel
from .Tutel import TutelOptions as TutelOptions

VERBOSE: bool = False
