from collections import namedtuple
from enum import Enum, auto

Token = namedtuple("Token", ["type", "value", "line", "column"])


# noinspection PyArgumentList
class TokenType(Enum):
    T_IDENTIFIER = auto()
    T_IF = auto()
    T_ELIF = auto()
    T_ELSE = auto()
    T_FOR = auto()
    T_WHILE = auto()
    T_RETURN = auto()
    T_PLUS = auto()
    T_MINUS = auto()
    T_MULTIPLY = auto()
    T_DIVIDE = auto()
    T_INT_DIVIDE = auto()
    T_MODULUS = auto()
    T_AND = auto()
    T_OR = auto()
    T_IN = auto()
    T_NOT = auto()
    T_LESS_THAN = auto()
    T_LESS_EQUAL_THAN = auto()
    T_GREATER_THAN = auto()
    T_GREATER_EQUAL_THAN = auto()
    T_EQUAL = auto()
    T_NOTEQUAL = auto()
    T_ASSIGNMENT = auto()
    T_PLUS_ASSIGNMENT = auto()
    T_MINUS_ASSIGNMENT = auto()
    T_MULTIPLY_ASSIGNMENT = auto()
    T_DIVIDE_ASSIGNMENT = auto()
    T_MODULUS_ASSIGNMENT = auto()
    T_TRUE = auto()
    T_FALSE = auto()
    T_NULL = auto()
    T_QUOTE = auto()
    T_DOUBLE_QUOTE = auto()
    T_COMMENT = auto()
    T_COLON = auto()
    T_SEMICOLON = auto()
    T_ESCAPE = auto()
    T_LEFT_BRACKET = auto()
    T_RIGHT_BRACKET = auto()
    T_LEFT_SQUARE_BRACKET = auto()
    T_RIGHT_SQUARE_BRACKET = auto()
    T_LEFT_CURLY_BRACKET = auto()
    T_RIGHT_CURLY_BRACKET = auto()
    T_DOT = auto()
    T_COMMA = auto()
    T_ETX = auto()
    T_TEXT_CONST = auto()
    T_NUMBER = auto()
    T_ILLEGAL = auto()
    T_UNKNOWN = auto()


keywords = {
    "if": TokenType.T_IF,
    "elif": TokenType.T_ELIF,
    "else": TokenType.T_ELSE,
    "for": TokenType.T_FOR,
    "while": TokenType.T_WHILE,
    "return": TokenType.T_RETURN,
    "and": TokenType.T_AND,
    "or": TokenType.T_OR,
    "in": TokenType.T_IN,
    "not": TokenType.T_NOT,
    "true": TokenType.T_TRUE,
    "false": TokenType.T_FALSE,
    "null": TokenType.T_NULL,
}

operators = {
    # Single characters
    "+": TokenType.T_PLUS,
    "-": TokenType.T_MINUS,
    "*": TokenType.T_MULTIPLY,
    "/": TokenType.T_DIVIDE,
    "%": TokenType.T_MODULUS,
    "<": TokenType.T_LESS_THAN,
    ">": TokenType.T_GREATER_THAN,
    "=": TokenType.T_ASSIGNMENT,

    ":": TokenType.T_COLON,
    ";": TokenType.T_SEMICOLON,
    "(": TokenType.T_LEFT_BRACKET,
    ")": TokenType.T_RIGHT_BRACKET,
    "[": TokenType.T_LEFT_SQUARE_BRACKET,
    "]": TokenType.T_RIGHT_SQUARE_BRACKET,
    "{": TokenType.T_LEFT_CURLY_BRACKET,
    "}": TokenType.T_RIGHT_CURLY_BRACKET,
    ".": TokenType.T_DOT,
    ",": TokenType.T_COMMA,

    # Double characters
    "<=": TokenType.T_LESS_EQUAL_THAN,
    ">=": TokenType.T_GREATER_EQUAL_THAN,
    "==": TokenType.T_EQUAL,
    "!=": TokenType.T_NOTEQUAL,
    "+=": TokenType.T_PLUS_ASSIGNMENT,
    "-=": TokenType.T_MINUS_ASSIGNMENT,
    "*=": TokenType.T_MULTIPLY_ASSIGNMENT,
    "/=": TokenType.T_DIVIDE_ASSIGNMENT,
    "//": TokenType.T_INT_DIVIDE,
    "%=": TokenType.T_MODULUS_ASSIGNMENT,
}


operator_parts = [
    "<", ">", "=", "!", "+", "-", "*", "/", "%", ":", ";", "(", ")", "[", "]", "{", "}", ".", ",",
]

escaped_chars = {
    'n': '\n',
    'r': '\r',
    't': '\t',
    '"': '"',
    '\'': '\'',
}
