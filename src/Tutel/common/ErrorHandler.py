import logging
import time

from Tutel.common.ErrorType import TutelException, TutelDebuggerException
from Tutel.core.InterpreterModule.Stack import Stack


def get_stack_trace(call_stack: Stack = None):
    if call_stack:
        trace = "Traceback (most recent call last):\n"
        for frame in call_stack:
            trace += f"\tFunction {frame.name}, line {frame.lineno}\n"
        return trace


class ErrorHandler:
    def __init__(self, module: str = "", level=logging.ERROR) -> None:
        self.logger = logging.getLogger(f"tutel_{module}_error_handler_{time.time()}")
        ch = logging.StreamHandler()
        ch.setLevel(level)
        formatter = logging.Formatter('%(message)s')
        ch.setFormatter(formatter)
        for handler in self.logger.handlers:
            self.logger.removeHandler(handler)
        self.logger.addHandler(ch)

    def handle_error(self, error: TutelException | TutelDebuggerException, call_stack: Stack = None) -> None:
        stack_trace = None
        if call_stack:
            stack_trace = get_stack_trace(call_stack)
        if stack_trace:
            self.logger.error(f"{stack_trace}{error}")
        else:
            self.logger.error(error)
        error.make_action()
