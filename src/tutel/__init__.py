__version__="1.0.0"

from .LexerModule.Lexer import Lexer as TutelLexer
from .ParserModule.Parser import Parser as TutelParser
from .InterpreterModule.Interpreter import Interpreter as TutelInterpreter
from .__main__ import main as execute
