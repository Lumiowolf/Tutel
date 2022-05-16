from LexerModule.Tokens import Token

MAX_IDENTIFIER_LENGTH = 64
MAX_TEXT_CONST_LENGTH = 1024
MAX_COMMENT_LENGTH = 1024
MAX_INTEGER = 2147483647


class LexerException(Exception):
    def __init__(self, token: Token) -> None:
        self.token = token
        self.base_msg = "Lexical error: "

    def make_action(self):
        raise self


class UnknownTokenLexerException(LexerException):
    def __str__(self) -> str:
        msg = f"{self.base_msg}" \
              f"symbol '{self.token.value}' " \
              f"at {self.token.line}:{self.token.column} " \
              f"is not recognized"
        return msg.encode("unicode-escape").decode()


class IdentifierTooLongLexerException(LexerException):
    def __str__(self) -> str:
        msg = f"{self.base_msg}" \
              f"identifier '{self.token.value}...' " \
              f"at {self.token.line}:{self.token.column} " \
              f"is too long (max length: {MAX_IDENTIFIER_LENGTH})"
        return msg.encode("unicode-escape").decode()


class CommentTooLongLexerException(LexerException):
    def __str__(self) -> str:
        msg = f"{self.base_msg}" \
              f"comment '{self.token.value}...' " \
              f"at {self.token.line}:{self.token.column} " \
              f"is too long (max length: {MAX_COMMENT_LENGTH})"
        return msg.encode("unicode-escape").decode()


class TextConstTooLongLexerException(LexerException):
    def __str__(self) -> str:
        msg = f"{self.base_msg}" \
              f"string '{self.token.value}...' " \
              f"at {self.token.line}:{self.token.column} " \
              f"is too long (max length: {MAX_TEXT_CONST_LENGTH})"
        return msg.encode("unicode-escape").decode()


class UnterminatedStringLexerException(LexerException):
    def __str__(self) -> str:
        msg = f"{self.base_msg}" \
              f"unterminated text const " \
              f"at {self.token.line}:{self.token.column}"
        return msg.encode("unicode-escape").decode()


class LeadingZerosInIntegerLexerException(LexerException):
    def __str__(self) -> str:
        msg = f"{self.base_msg}" \
              f"leading zeros in integer " \
              f"at {self.token.line}:{self.token.column} " \
              f"are not allowed"
        return msg.encode("unicode-escape").decode()


class IntegerTooLargeLexerException(LexerException):
    def __str__(self) -> str:
        msg = f"{self.base_msg}" \
              f"integer " \
              f"at {self.token.line}:{self.token.column} " \
              f"is too large (max: {MAX_INTEGER})"
        return msg.encode("unicode-escape").decode()


class UnknownEscapingLexerException(LexerException):
    def __str__(self) -> str:
        msg = f"{self.base_msg}" \
              f"unknown escaped character '{self.token.value}' " \
              f"at {self.token.line}:{self.token.column}"
        return msg.encode("unicode-escape").decode()


class ParserException(Exception):
    def __init__(self, method: str, token: Token) -> None:
        self.method = method
        self.token = token
        self.base_msg = "Syntax error: "

    def make_action(self):
        raise self


class MissingLeftBracketException(ParserException):
    def __str__(self) -> str:
        msg = f"{self.base_msg}" \
              f"{self.method}: " \
              "missing '(', " \
              f"instead got '{self.token.value}' " \
              f"at {self.token.line}:{self.token.column}"
        return msg.encode("unicode-escape").decode()


class MissingRightBracketException(ParserException):
    def __str__(self) -> str:
        msg = f"{self.base_msg}" \
              f"{self.method}: " \
              "missing ')', " \
              f"instead got '{self.token.value}' " \
              f"at {self.token.line}:{self.token.column}"
        return msg.encode("unicode-escape").decode()


class MissingIdentifierAfterCommaException(ParserException):
    def __str__(self) -> str:
        msg = f"{self.base_msg}" \
              f"{self.method}: " \
              "missing identifier after comma, " \
              f"instead got '{self.token.value}' " \
              f"at {self.token.line}:{self.token.column}"
        return msg.encode("unicode-escape").decode()


class MissingExpressionAfterCommaException(ParserException):
    def __str__(self) -> str:
        msg = f"{self.base_msg}" \
              f"{self.method}: " \
              "missing expression after comma, " \
              f"instead got '{self.token.value}' " \
              f"at {self.token.line}:{self.token.column}"
        return msg.encode("unicode-escape").decode()


class MissingRightCurlyBracketException(ParserException):
    def __str__(self) -> str:
        msg = f"{self.base_msg}" \
              f"{self.method}: " \
              "missing '}', " \
              f"instead got '{self.token.value}' " \
              f"at {self.token.line}:{self.token.column}"
        return msg.encode("unicode-escape").decode()


class MissingSemicolonException(ParserException):
    def __str__(self) -> str:
        msg = f"{self.base_msg}" \
              f"{self.method}: " \
              "missing ';', " \
              f"instead got '{self.token.value}' " \
              f"at {self.token.line}:{self.token.column}"
        return msg.encode("unicode-escape").decode()


class MissingRightSideOfAssignmentException(ParserException):
    def __str__(self) -> str:
        msg = f"{self.base_msg}" \
              f"{self.method}: " \
              "missing right side of expression" \
              f"at {self.token.line}:{self.token.column}"
        return msg.encode("unicode-escape").decode()


class MissingConditionException(ParserException):
    def __str__(self) -> str:
        msg = f"{self.base_msg}" \
              f"{self.method}: " \
              "missing statement condition" \
              f"at {self.token.line}:{self.token.column}"
        return msg.encode("unicode-escape").decode()


class MissingBodyException(ParserException):
    def __str__(self) -> str:
        msg = f"{self.base_msg}" \
              f"{self.method}: " \
              "missing statement body" \
              f"at {self.token.line}:{self.token.column}"
        return msg.encode("unicode-escape").decode()


class MissingIteratorException(ParserException):
    def __str__(self) -> str:
        msg = f"{self.base_msg}" \
              f"{self.method}: " \
              "missing iterator" \
              f"at {self.token.line}:{self.token.column}"
        return msg.encode("unicode-escape").decode()


class MissingIterableException(ParserException):
    def __str__(self) -> str:
        msg = f"{self.base_msg}" \
              f"{self.method}: " \
              "missing iterable" \
              f"at {self.token.line}:{self.token.column}"
        return msg.encode("unicode-escape").decode()


class MissingKeywordInException(ParserException):
    def __str__(self) -> str:
        msg = f"{self.base_msg}" \
              f"{self.method}: " \
              "missing 'in' keyword " \
              f"at {self.token.line}:{self.token.column}"
        return msg.encode("unicode-escape").decode()


class ExprMissingRightSideException(ParserException):
    def __str__(self) -> str:
        msg = f"{self.base_msg}" \
              f"{self.method}: " \
              "missing right side of expression " \
              f"at {self.token.line}:{self.token.column}"
        return msg.encode("unicode-escape").decode()


class MissingIdentifierAfterDotException(ParserException):
    def __str__(self) -> str:
        msg = f"{self.base_msg}" \
              f"{self.method}: " \
              "missing identifier after dot operator " \
              f"at {self.token.line}:{self.token.column}"
        return msg.encode("unicode-escape").decode()


class MissingRightSquereBracketException(ParserException):
    def __str__(self) -> str:
        msg = f"{self.base_msg}" \
              f"{self.method}: " \
              "missing ']', " \
              f"instead got '{self.token.value}' " \
              f"at {self.token.line}:{self.token.column}"
        return msg.encode("unicode-escape").decode()
