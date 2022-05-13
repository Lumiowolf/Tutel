from typing import TextIO


class Source:
    def __init__(self, source: TextIO):
        self.source = source
        self.line = 1
        self.column = 0
        self.next = self.source.read(1)
        self.char = ""
        self.get_next_char()

    def get_next_char(self):
        if self.char == '\n':
            if self.next == '\r':
                self._get_next()
                self.char = '\n'
            self.line += 1
            self.column = 1
        elif self.char == '\r':
            self._get_next()
            if self.next == '\n':
                self._get_next()
            self.line += 1
            self.column = 1
        elif self.next == '':
            self.next = '\x03'
            self.column += 1
        else:
            self.column += 1
        self._get_next()

    def _get_next(self):
        self.char = self.next
        self.next = self.source.read(1)
