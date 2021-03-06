from Tutel.LexerModule.Tokens import Token

MAX_IDENTIFIER_LENGTH = 64
MAX_TEXT_CONST_LENGTH = 1024
MAX_COMMENT_LENGTH = 1024
MAX_INTEGER = 2147483647


class TutelException(Exception):
    def make_action(self):
        raise self


class Exit(TutelException):
    pass


####################
# Lexer exceptions #
####################


class LexerException(TutelException):
    def __init__(self, token: Token) -> None:
        self.token = token
        self.base_msg = "Lexical error: "


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


#####################
# Parser exceptions #
#####################


class ParserException(TutelException):
    def __init__(self, method: str, token: Token) -> None:
        self.method = method
        self.token = token
        self.base_msg = "Syntax error: "


class MissingFunctionBlockException(ParserException):
    def __str__(self) -> str:
        msg = f"{self.base_msg}" \
              f"{self.method}: " \
              "missing 'function body (block or statement) " \
              f"instead got '{self.token.value}' " \
              f"at {self.token.line}:{self.token.column}"
        return msg.encode("unicode-escape").decode()


class FunctionRedefinitionException(ParserException):
    def __str__(self) -> str:
        msg = f"{self.base_msg}" \
              f"{self.method}: " \
              f"redefinition of function '{self.token.value}' " \
              f"at {self.token.line}:{self.token.column}"
        return msg.encode("unicode-escape").decode()


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
              "missing statement body " \
              f"at {self.token.line}:{self.token.column}"
        return msg.encode("unicode-escape").decode()


class MissingIteratorException(ParserException):
    def __str__(self) -> str:
        msg = f"{self.base_msg}" \
              f"{self.method}: " \
              "missing iterator" \
              f"at {self.token.line}:{self.token.column}"
        return msg.encode("unicode-escape").decode()


class MissingKeywordInException(ParserException):
    def __str__(self) -> str:
        msg = f"{self.base_msg}" \
              f"{self.method}: " \
              "missing 'in' keyword " \
              f"at {self.token.line}:{self.token.column}"
        return msg.encode("unicode-escape").decode()


class MissingIterableException(ParserException):
    def __str__(self) -> str:
        msg = f"{self.base_msg}" \
              f"{self.method}: " \
              "missing iterable" \
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


class MissingRightSquareBracketException(ParserException):
    def __str__(self) -> str:
        msg = f"{self.base_msg}" \
              f"{self.method}: " \
              "missing ']', " \
              f"instead got '{self.token.value}' " \
              f"at {self.token.line}:{self.token.column}"
        return msg.encode("unicode-escape").decode()


##########################
# Interpreter exceptions #
##########################


class InterpreterException(TutelException):
    def __init__(self) -> None:
        self.base_msg = "Execution error: "


class NotIterableException(InterpreterException):
    def __init__(self, type_name) -> None:
        super().__init__()
        self.type_name = type_name

    def __str__(self) -> str:
        msg = f"{self.base_msg}" \
              f"'{self.type_name}' " \
              "object is not iterable"
        return msg.encode("unicode-escape").decode()


class CannotAssignException(InterpreterException):
    def __init__(self, value) -> None:
        super().__init__()
        self.value = value

    def __str__(self) -> str:
        msg = f"{self.base_msg}" \
              f"object at {self.value.position[0]}:{self.value.position[1]} " \
              "is not assignable"
        return msg.encode("unicode-escape").decode()


class NotDefinedException(InterpreterException):
    def __init__(self, name) -> None:
        super().__init__()
        self.name = name

    def __str__(self) -> str:
        msg = f"{self.base_msg}" \
              f"'{self.name}' " \
              "is not defined"
        return msg.encode("unicode-escape").decode()


class UnsupportedOperandException(InterpreterException):
    def __init__(self, l_type, r_type, operator) -> None:
        super().__init__()
        self.l_type = l_type
        self.r_type = r_type
        self.operator = operator

    def __str__(self) -> str:
        msg = f"{self.base_msg}" \
              f"unsupported operand type(s) for {self.operator}: " \
              f"{self.l_type} and {self.r_type}"
        return msg.encode("unicode-escape").decode()


class BadOperandForUnaryException(InterpreterException):
    def __init__(self, type_name) -> None:
        super().__init__()
        self.type = type_name

    def __str__(self) -> str:
        msg = f"{self.base_msg}" \
              f"bad operand type for unary -: {self.type}"
        return msg.encode("unicode-escape").decode()


class AttributeException(InterpreterException):
    def __init__(self, type_name, value) -> None:
        super().__init__()
        self.type_name = type_name
        self.value = value

    def __str__(self) -> str:
        msg = f"{self.base_msg}" \
              f"'{self.type_name}' object has no attribute '{self.value}'"
        return msg.encode("unicode-escape").decode()


class MismatchedArgsCountException(InterpreterException):
    def __init__(self, fun_name, got_number=None, expected_number=None) -> None:
        super().__init__()
        self.fun_name = fun_name
        self.expected_number = expected_number
        self.got_number = got_number

    def __str__(self) -> str:
        if self.expected_number is None:
            msg = f"{self.base_msg}" \
                  f"{self.fun_name}() got wrong number of arguments"
        else:
            msg = f"{self.base_msg}" \
                  f"{self.fun_name}() takes {self.expected_number} arguments but {self.got_number} were given"
        return msg.encode("unicode-escape").decode()


class OutOfRangeException(InterpreterException):
    def __str__(self) -> str:
        msg = f"{self.base_msg}" \
              f"list index out of range"
        return msg.encode("unicode-escape").decode()


class UnknownException(InterpreterException):
    def __init__(self, e: Exception) -> None:
        super().__init__()
        self.exception = e

    def __str__(self) -> str:
        msg = f"{self.base_msg}" \
              f"unknown exception occurred (probably caused by builtin function), " \
              f"message: {self.exception}"
        return msg.encode("unicode-escape").decode()


class NothingToRunException(InterpreterException):
    def __str__(self) -> str:
        msg = f"{self.base_msg}" \
              f"nothing to run"
        return msg.encode("unicode-escape").decode()


class RecursionException(InterpreterException):
    def __str__(self) -> str:
        msg = f"{self.base_msg}" \
              f"maximum recursion depth exceeded"
        return msg.encode("unicode-escape").decode()
