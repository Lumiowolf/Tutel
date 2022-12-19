__version__ = "1.0.11"

from .InterpreterModule.Interpreter import Interpreter as TutelInterpreter
from .LexerModule.Lexer import Lexer as TutelLexer
from .ParserModule.Parser import Parser as TutelParser
from .runner import main as execute
