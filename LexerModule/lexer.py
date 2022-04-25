from io import StringIO

from LexerModule import error_handler
from LexerModule.tokens import *

MAX_IDENTIFIER_LENGTH = 64


class Lexer:
    def __init__(self, source: StringIO):
        self._error_handler = error_handler.ErrorHandler(self)
        self.line = 0
        self.position = 0
        self.token = None
        self.source = source
        self.char = ""
        self._get_next_char()
        self.position = 0

    def _get_next_char(self) -> None:
        self.char = self.source.read(1)
        self.position += 1

    def get_next_token(self) -> Token:
        while self._skip_whites():
            pass

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

        # Operators are being build greedily
        if self._try_build_operator():
            return self.token
        # Punctuation marks are being build lazily
        if self._try_build_punctuation():
            return self.token

        self.token = Token(TokenType.T_UNKNOWN, self.char, self.line, self.position)
        self._get_next_char()
        self._error_handler.handle_unknown()
        return self.token

    def _skip_whites(self) -> bool:
        if self.char == '\n':
            self._get_next_char()
            if self.char == '\r':
                self._get_next_char()
            self.line += 1
            self.position = 0
            return True
        if self.char == '\r':
            self._get_next_char()
            if self.char == '\n':
                self._get_next_char()
            self.line += 1
            self.position = 0
            return True
        if self.char.isspace():
            self._get_next_char()
            return True
        return False

    def _try_build_etx(self) -> bool:
        if self.char in ['\x03', '']:  # \x03 is ETX
            self.token = Token(TokenType.T_ETX, '\x03', self.line, self.position)
            # self._get_next_char()
            return True
        return False

    def _try_build_comment(self) -> bool:
        if self.char == "#":
            starting_at = self.position
            self._get_next_char()
            comment = []
            while not self._try_build_etx() and self.char not in ['\n', '\r']:
                comment.append(self.char)
                self._get_next_char()
            comment = "".join(comment)
            self.token = Token(TokenType.T_COMMENT, comment, self.line, starting_at)
            return True
        return False

    def _try_build_identifier_or_keyword(self) -> bool:
        if self.char.isalpha() or self.char == "_":
            starting_at = self.position
            identifier = [self.char]
            length = 1
            self._get_next_char()
            while self.char.isalnum() or self.char == "_":
                if length <= MAX_IDENTIFIER_LENGTH:
                    identifier.append(self.char)
                    length += 1
                self._get_next_char()
            identifier = "".join(identifier)
            if length <= MAX_IDENTIFIER_LENGTH:
                if identifier in keywords.keys():
                    # Keyword
                    self.token = Token(keywords[identifier], identifier, self.line, starting_at)
                else:
                    # Identifier
                    self.token = Token(TokenType.T_IDENTIFIER, identifier, self.line, starting_at)
            else:
                self.token = Token(TokenType.T_ILLEGAL, identifier + "...", self.line, starting_at)
                self._error_handler.handle_too_long()
            return True
        return False

    def _try_build_text_const(self) -> bool:
        if self.char in ['"', '\'']:
            starting_at = self.position
            surrounded_by = self.char
            text_const = []
            self._get_next_char()
            while self.char != surrounded_by:
                if self.char in ['\n', '\r', '\3']:
                    self.token = Token(TokenType.T_ILLEGAL, self.char, self.line, self.position)
                    self._error_handler.handle_illegal()
                    return True
                if self.char == "\\":
                    self._get_next_char()
                    text_const.append(
                        special_escaping[self.char] if self.char in special_escaping.keys() else self.char
                    )
                else:
                    text_const.append(self.char)
                self._get_next_char()
            text_const = "".join(text_const)
            self._get_next_char()
            self.token = Token(TokenType.T_TEXT_CONST, text_const, self.line, starting_at)
            return True
        return False

    def _try_build_number(self) -> bool:
        if self.char.isnumeric():
            starting_at = self.position
            number = int(self.char)
            self._get_next_char()
            while self.char.isnumeric():
                if number == 0 and int(self.char) != 0:
                    self.token = Token(TokenType.T_ILLEGAL, self.char, self.line, self.position)
                    self._error_handler.handle_illegal()
                    return True
                number *= 10
                number += int(self.char)
                self._get_next_char()
            self.token = Token(TokenType.T_NUMBER, number, self.line, starting_at)
            return True
        return False

    def _try_build_operator(self) -> bool:
        if self.char in operator_parts:
            starting_at = self.position
            operator = [self.char]
            self._get_next_char()
            while self.char in operator_parts:
                operator.append(self.char)
                self._get_next_char()
            operator = "".join(operator)
            if operator in operators.keys():
                self.token = Token(
                    operators[operator],
                    operator,
                    self.line,
                    starting_at
                )
                return True
            else:
                self.token = Token(TokenType.T_UNKNOWN, operator, self.line, starting_at)
                self._error_handler.handle_unknown()
                return True
        return False

    def _try_build_punctuation(self) -> bool:
        if self.char in punctuations.keys():
            self.token = Token(
                punctuations[self.char],
                self.char,
                self.line,
                self.position
            )
            self._get_next_char()
            return True
        return False
