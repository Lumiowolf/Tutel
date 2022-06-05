from typing import TextIO

from ErrorHandlerModule.ErrorHandler import ErrorHandler
from ErrorHandlerModule.ErrorType import (
    UnknownTokenLexerException,
    CommentTooLongLexerException,
    IdentifierTooLongLexerException,
    UnterminatedStringLexerException,
    TextConstTooLongLexerException,
    UnknownEscapingLexerException,
    LeadingZerosInIntegerLexerException,
    IntegerTooLargeLexerException,
    MAX_IDENTIFIER_LENGTH,
    MAX_TEXT_CONST_LENGTH,
    MAX_COMMENT_LENGTH,
    MAX_INTEGER,
)
from LexerModule.Source import Source
from LexerModule.Tokens import *


class Lexer:
    def __init__(self, source: TextIO, error_handler: ErrorHandler):
        self.starting_at_line = None
        self.starting_at_column = None
        self._error_handler = error_handler
        self.token = None
        self.source = Source(source)

    def get_next_token(self) -> Token:
        self._skip_whites()

        self.starting_at_line = self.source.line
        self.starting_at_column = self.source.column
        if self._try_build_etx():
            return self.token
        if self._try_build_comment():
            return self.token
        if self._try_build_identifier_or_keyword():
            return self.token
        if self._try_build_text_const():
            return self.token
        if self._try_build_number():
            return self.token

        if self._try_build_operator():
            return self.token

        self.token = Token(TokenType.T_UNKNOWN, self.source.char, self.source.line, self.source.column)
        self._error_handler.handler_error(UnknownTokenLexerException(self.token))

    def _skip_whites(self) -> None:
        while self.source.char.isspace():
            self.source.get_next_char()

    def _try_build_etx(self) -> bool:
        if self.source.char == '\x03':  # \x03 is ETX
            self.token = Token(TokenType.T_ETX, '\x03', self.source.line, self.starting_at_column)
            return True
        return False

    def _try_build_comment(self) -> bool:
        if self.source.char == "#":
            self.source.get_next_char()
            comment = []
            while self.source.char not in ['\n', '\x03'] and len(comment) <= MAX_COMMENT_LENGTH:
                comment.append(self.source.char)
                self.source.get_next_char()
            comment = "".join(comment)
            if len(comment) > MAX_COMMENT_LENGTH:
                comment = comment[:-1]
                self.token = Token(TokenType.T_ILLEGAL, comment, self.source.line, self.starting_at_column)
                self._error_handler.handler_error(CommentTooLongLexerException(self.token))
            self.token = Token(TokenType.T_COMMENT, comment, self.source.line, self.starting_at_column)
            return True
        return False

    def _try_build_identifier_or_keyword(self) -> bool:
        if self.source.char.isalpha() or self.source.char == "_":
            identifier = [self.source.char]
            self.source.get_next_char()
            while self.source.char.isalnum() or self.source.char == "_" and len(identifier) <= MAX_IDENTIFIER_LENGTH:
                identifier.append(self.source.char)
                self.source.get_next_char()
            identifier = "".join(identifier)
            if len(identifier) > MAX_IDENTIFIER_LENGTH:
                identifier = identifier[:-1]
                self.token = Token(TokenType.T_ILLEGAL, identifier, self.source.line, self.starting_at_column)
                self._error_handler.handler_error(IdentifierTooLongLexerException(self.token))
            if tokenType := keywords.get(identifier):
                # Keyword
                self.token = Token(tokenType, identifier, self.source.line, self.starting_at_column)
            else:
                # Identifier
                self.token = Token(TokenType.T_IDENTIFIER, identifier, self.source.line, self.starting_at_column)
            return True
        return False

    def _try_build_text_const(self) -> bool:
        if self.source.char in ['"', '\'']:
            surrounded_by = self.source.char
            text_const = []
            self.source.get_next_char()
            while self.source.char != surrounded_by and len(text_const) <= MAX_TEXT_CONST_LENGTH:
                if self.source.char in ['\n', '\3']:
                    self.token = Token(TokenType.T_ILLEGAL, "".join(text_const + [self.source.char]), self.source.line,
                                       self.source.column)
                    self._error_handler.handler_error(UnterminatedStringLexerException(self.token))
                if self.source.char == "\\":
                    self.source.get_next_char()
                    if escaped := escaped_chars.get(self.source.char):
                        text_const.append(escaped)
                    else:
                        self.token = Token(TokenType.T_ILLEGAL, "\\" + self.source.char,
                                           self.source.line, self.source.column - 1)
                        self._error_handler.handler_error(UnknownEscapingLexerException(self.token))
                else:
                    text_const.append(self.source.char)
                self.source.get_next_char()
            text_const = "".join(text_const)
            if len(text_const) > MAX_TEXT_CONST_LENGTH:
                text_const = text_const[:-1]
                self.token = Token(TokenType.T_ILLEGAL, text_const, self.source.line, self.starting_at_column)
                self._error_handler.handler_error(TextConstTooLongLexerException(self.token))
            self.source.get_next_char()
            self.token = Token(TokenType.T_TEXT_CONST, text_const, self.source.line, self.starting_at_column)
            return True
        return False

    def _try_build_number(self) -> bool:
        if self.source.char.isdecimal():
            number = int(self.source.char)
            self.source.get_next_char()
            while self.source.char.isdecimal() and number <= MAX_INTEGER:
                if number == 0 and int(self.source.char) != 0:
                    self.token = Token(TokenType.T_ILLEGAL, self.source.char, self.source.line, self.source.column)
                    self._error_handler.handler_error(LeadingZerosInIntegerLexerException(self.token))
                number *= 10
                number += int(self.source.char)
                self.source.get_next_char()
            if number > MAX_INTEGER:
                self.token = Token(TokenType.T_ILLEGAL, number, self.source.line, self.starting_at_column)
                self._error_handler.handler_error(IntegerTooLargeLexerException(self.token))
            self.token = Token(TokenType.T_NUMBER, number, self.source.line, self.starting_at_column)
            return True
        return False

    def _try_build_operator(self) -> bool:
        if self.source.char in operator_parts:
            operator = [self.source.char]
            self.source.get_next_char()
            while "".join(operator + [self.source.char]) in operators.keys():
                operator.append(self.source.char)
                self.source.get_next_char()
            operator = "".join(operator)
            self.token = Token(operators[operator], operator, self.source.line, self.starting_at_column)
            return True
        return False
