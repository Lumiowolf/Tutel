import logging
import time

from Tutel.ErrorHandlerModule.ErrorType import TutelException


class ErrorHandler:
    def __init__(self, level=logging.ERROR) -> None:
        self.logger = logging.getLogger(f"tutel_error_handler_{time.time()}")
        ch = logging.StreamHandler()
        ch.setLevel(level)
        formatter = logging.Formatter('%(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def handle_error(self, error: TutelException) -> None:
        self.logger.error(error)
        error.make_action()
