import logging
import time

from ErrorHandlerModule.ErrorType import LexerException, ParserException


class ErrorHandler:
    def __init__(self):
        self.logger = logging.getLogger(f"lexer_error_handler_{time.time()}")
        ch = logging.StreamHandler()
        ch.setLevel(logging.ERROR)
        formatter = logging.Formatter('%(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def handler_error(self, error: LexerException | ParserException):
        self.logger.error(error)
        error.make_action()
