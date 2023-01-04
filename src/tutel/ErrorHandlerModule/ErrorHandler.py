import logging
import time

from tutel.ErrorHandlerModule.ErrorType import TutelException
from tutel.InterpreterModule.StackFrame import StackFrame


class ErrorHandler:
    def __init__(self, module: str = "", level=logging.ERROR, stack: list[StackFrame] = None) -> None:
        self.logger = logging.getLogger(f"tutel_{module}_error_handler_{time.time()}")
        ch = logging.StreamHandler()
        ch.setLevel(level)
        formatter = logging.Formatter('%(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        self.stack = stack

    def handle_error(self, error: TutelException) -> None:
        stack_trace = self.get_stack_trace()
        if stack_trace:
            self.logger.error(f"{stack_trace}{error}")
        else:
            self.logger.error(error)
        error.make_action()

    def get_stack_trace(self):
        if self.stack:
            trace = "Traceback (most recent call last):\n"
            for frame in self.stack:
                trace += f"\tFunction {frame.name}, line {frame.lineno}\n"
            return trace
