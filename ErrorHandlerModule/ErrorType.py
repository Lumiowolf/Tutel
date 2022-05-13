from LexerModule.Tokens import Token


class LexerException(Exception):
    def __init__(self, token: Token) -> None:
        self.token = token


class UnknownTokenLexerException(LexerException):
    def __repr__(self) -> str:
        msg = f"Syntax error: " \
              f"symbol '{self.token.value}' " \
              f"at {self.token.line}:{self.token.column} " \
              f"is not recognized"
        return msg.encode("unicode-escape").decode()


class IdentifierTooLongLexerException(LexerException):
    def __repr__(self) -> str:
        msg = f"Syntax error: " \
              f"identifier '{self.token.value}...' " \
              f"at {self.token.line}:{self.token.column} " \
              f"is too long (max length: {MAX_IDENTIFIER_LENGTH})"
        return msg.encode("unicode-escape").decode()


class CommentTooLongLexerException(LexerException):
    def __repr__(self) -> str:
        msg = f"Syntax error: " \
              f"comment '{self.token.value}...' " \
              f"at {self.token.line}:{self.token.column} " \
              f"is too long (max length: {MAX_COMMENT_LENGTH})"
        return msg.encode("unicode-escape").decode()


class TextConstTooLongLexerException(LexerException):
    def __repr__(self) -> str:
        msg = f"Syntax error: " \
              f"string '{self.token.value}...' " \
              f"at {self.token.line}:{self.token.column} " \
              f"is too long (max length: {MAX_TEXT_CONST_LENGTH})"
        return msg.encode("unicode-escape").decode()


class UnterminatedStringLexerException(LexerException):
    def __repr__(self) -> str:
        msg = f"Syntax error: " \
              f"unterminated text const " \
              f"at {self.token.line}:{self.token.column}"
        return msg.encode("unicode-escape").decode()


class LeadingZerosInIntegerLexerException(LexerException):
    def __repr__(self) -> str:
        msg = f"Syntax error: " \
              f"leading zeros in integer " \
              f"at {self.token.line}:{self.token.column} " \
              f"are not allowed"
        return msg.encode("unicode-escape").decode()


class IntegerTooLargeLexerException(LexerException):
    def __repr__(self) -> str:
        msg = f"Syntax error: " \
              f"integer " \
              f"at {self.token.line}:{self.token.column} " \
              f"is too large (max: {MAX_INTEGER})"
        return msg.encode("unicode-escape").decode()


class UnknownEscapingLexerException(LexerException):
    def __repr__(self) -> str:
        msg = f"Syntax error: " \
              f"unknown escaped character '{self.token.value}' " \
              f"at {self.token.line}:{self.token.column}"
        return msg.encode("unicode-escape").decode()


MAX_IDENTIFIER_LENGTH = 64
MAX_TEXT_CONST_LENGTH = 1024
MAX_COMMENT_LENGTH = 1024
MAX_INTEGER = 2147483647
