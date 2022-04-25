import logging
import time

from LexerModule import lexer


class ErrorHandler:
    def __init__(self, lexer):
        self.lexer = lexer

        self.logger = logging.getLogger(f"lexer_error_handler_{time.time()}")
        ch = logging.StreamHandler()
        ch.setLevel(logging.ERROR)
        formatter = logging.Formatter('%(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def handle_illegal(self) -> None:
        msg = f"Syntax error: " \
              f"symbol '{self.lexer.token.value}' " \
              f"at {self.lexer.token.line}:{self.lexer.token.position} " \
              f"is not allowed here"
        self.logger.error(msg.encode("unicode-escape").decode())

    def handle_unknown(self) -> None:
        msg = f"Syntax error: " \
              f"symbol '{self.lexer.token.value}' " \
              f"at {self.lexer.token.line}:{self.lexer.token.position} " \
              f"is not recognized"
        self.logger.error(msg.encode("unicode-escape").decode())

    def handle_too_long(self) -> None:
        msg = f"Syntax error: " \
              f"identifier '{self.lexer.token.value}' " \
              f"at {self.lexer.token.line}:{self.lexer.token.position} " \
              f"is too long (max length: {lexer.MAX_IDENTIFIER_LENGTH})"
        self.logger.error(msg.encode("unicode-escape").decode())
