from collections import namedtuple
from enum import Enum, auto

from Tutel.common.Source import Source

ETX = '\x03'

Token = namedtuple("Token", ["type", "value"])


class RequestTokenType(Enum):
    T_WORD = auto()
    T_NUMBER = auto()
    T_ETX = auto()
    T_UNKNOWN = auto()


class RequestLexer:
    def __init__(self, source):
        self.token = None
        self.source = Source(source)

    def get_next_token(self):
        self._skip_whites()

        if self._try_build_etx():
            return self.token
        if self._try_build_word():
            return self.token
        if self._try_build_number():
            return self.token

        self.token = Token(RequestTokenType.T_UNKNOWN, self.source.char)

    def _skip_whites(self) -> None:
        while self.source.char.isspace():
            self.source.get_next_char()

    def _try_build_etx(self) -> bool:
        if self.source.char == ETX:  # \x03 is ETX
            self.token = Token(RequestTokenType.T_ETX, ETX)
            return True
        return False

    def _try_build_word(self) -> bool:
        if self.source.char.isalpha():
            word = [self.source.char]
            self.source.get_next_char()
            # while self.source.char.isalpha() or self.source.char in "_.-":
            while not self.source.char.isspace() and self.source.char not in [ETX]:
                word.append(self.source.char)
                self.source.get_next_char()
            word = "".join(word)
            self.token = Token(RequestTokenType.T_WORD, word)
            return True
        return False

    def _try_build_number(self) -> bool:
        if self.source.char.isdecimal():
            number = int(self.source.char)
            self.source.get_next_char()
            while self.source.char.isdecimal():
                number *= 10
                number += int(self.source.char)
                self.source.get_next_char()
            self.token = Token(RequestTokenType.T_NUMBER, number)
            return True
        return False
