import os
import threading
from enum import auto, Enum
from io import StringIO
from time import sleep
from typing import Callable

from Tutel import debugger
from Tutel.common.ErrorHandler import ErrorHandler
from Tutel.common.ErrorType import InterpreterException, Stop, TutelException
from Tutel.core.InterpreterModule.Interpreter import Interpreter
from Tutel.core.InterpreterModule.StackFrame import StackFrame
from Tutel.core.LexerModule.Lexer import get_bp_possible_lines, Lexer
from Tutel.core.ParserModule.Classes import Visited
from Tutel.core.ParserModule.Parser import Parser
from Tutel.core.Runner.TutelOptions import TutelOptions
from Tutel.core.Runner.TutelRunner import TutelRunner


class StopEvent(Enum):
    Breakpoint = auto()
    StepInto = auto()
    StepOver = auto()
    Pause = auto()


class InterpreterThread(threading.Thread):
    def __init__(self, exec_fun: Callable, exec_args: tuple, handle_error: Callable, post_exec: Callable):
        super().__init__(name="Interpreter")
        self.exec_fun = exec_fun
        self.exec_args = exec_args
        self.handle_error = handle_error
        self.post_exec = post_exec

    def run(self) -> None:
        try:
            self.exec_fun(*self.exec_args)
            self.post_exec()
        except Stop:
            self.post_exec()
        except InterpreterException as e:
            self.handle_error(e)


class TutelDebugger(TutelRunner):
    def __init__(self, filename: str = None,
                 options: TutelOptions = None,
                 error_handler: ErrorHandler = None):
        super().__init__(None, options)
        self.error_handler = error_handler or ErrorHandler(module="debugger")
        self.bp_possible_lines: dict[str, set[int]] = {}
        self.breakpoints: dict[str, dict[int, Visited | None]] = {}
        # self.expr_breakpoints: dict[str, list[tuple[int, Visited]]] = {}
        self.interpreter = Interpreter(debug_callback=self.check_line)
        self.step_into_mode = False
        self.step_over_mode = False
        self.watched_frame = None
        self.pause_mode = False
        self.filename = filename

        if self.filename:
            self.breakpoints[self.filename] = {}
            with open(self.filename, "r") as file:
                self.code = file.read()
            self.bp_possible_lines[self.filename] = get_bp_possible_lines(self.code)
        if debugger.DEBUGGER_OUT:
            with open(debugger.DEBUGGER_OUT, "w"):
                pass

    def message(self, msg):
        pass

    def start(self):
        self.run()

    def _clean_up(self):
        self.step_into_mode = False
        self.step_over_mode = False
        self.watched_frame = None
        self.pause_mode = False
        # print("clean up")
        self.interpreter.clean_up()
        if self.options.gui_out_path:
            with open(self.options.gui_out_path, "a") as file:
                file.write('\n')
                sleep(1)
                file.write('\n')

    def run(self) -> bool:
        if not self.is_source_code_set():
            return False
        try:
            self._prepare_to_run(debug=True)
        except TutelException as e:
            self._post_morten(e)
            return False
        if self.options.gui_out_path:
            with open(self.options.gui_out_path, "w"):
                pass
        thread = InterpreterThread(
            exec_fun=self.interpreter.execute,
            exec_args=(self.program, "main"),
            handle_error=self._post_morten,
            post_exec=self._clean_up,
        )
        thread.start()

        return True

    def check_line(self):
        if self.step_into_mode:
            self._break(StopEvent.StepInto)
        elif self.step_over_mode and self.interpreter.dropped_frame and self.interpreter.dropped_frame.index == self.watched_frame:
            self._break(StopEvent.StepOver)
        elif self.interpreter.lineno in self.breakpoints[self.filename]:
            self._break(StopEvent.Breakpoint)

    def _break(self, _type: StopEvent):
        self.message(f"Program stopped in function {self.interpreter.curr_frame.name} "
                     f"at line {self.interpreter.curr_frame.lineno}")

    def _post_morten(self, e: TutelException):
        self.message(f"Program raised exception: '{e}'. Entering post mortem mode.")

    def is_source_code_set(self) -> bool:
        if self.filename is None:
            return False
        if self.breakpoints.get(self.filename) is not None and self.bp_possible_lines.get(self.filename) is not None:
            return True
        self.message(f"Source code not provided. Use command 'file' to set source code.")
        return False

    def get_bp_lines(self):
        if not self.is_source_code_set():
            return False, "Source code not provided."

        self.message(f"Breakpoints can be set at lines: {self.bp_possible_lines[self.filename]}")

        return True, sorted(list(self.bp_possible_lines[self.filename]))

    def stack(self) -> tuple[bool, str | list[StackFrame]]:
        if not self.is_source_code_set():
            return False, "Source code not provided."

        stack = list(reversed(self.interpreter.call_stack))
        for frame in stack:
            frame.file = self.filename
        if not stack:
            self.message("Stack is empty.")
        else:
            self.message(stack)

        return True, stack

    def frame(self, index: int) -> tuple[bool, StackFrame | str]:
        if not self.is_source_code_set():
            return False, "Source code not provided."

        if index not in range(len(self.interpreter.call_stack)):
            msg = f"Stack index out of range, stack size is {len(self.interpreter.call_stack)}."
            self.message(msg)
            return False, msg

        frame = list(reversed(self.interpreter.call_stack))[index]
        frame.file = self.filename
        self.message(frame)
        return True, frame

    def get_breakpoints(self, file: str) -> tuple[bool, list[int] | str]:
        file = os.path.realpath(file)
        if (bps := self.breakpoints.get(file)) is not None:
            if len(bps) > 0:
                self.message(f"Breakpoints are set at lines: {list(bps)}.")
            else:
                self.message(f"There are no breakpoints set.")
            print(bps)
            return True, list(bps)
        else:
            return False, "Unknown error occurred during setting breakpoint"

    def set_breakpoint(self, file: str, line: int, expr: str = None) -> tuple[bool, int | str]:
        file = os.path.realpath(file)
        if self.bp_possible_lines.get(file) is not None and line not in self.bp_possible_lines.get(file):
            msg = f"Could not set breakpoint at line {line}"
            self.message(msg)
            return False, msg
        else:
            if file not in self.breakpoints:
                self.breakpoints[file] = {}
            if expr:
                parser = Parser()
                parser.lexer = Lexer(StringIO(expr))
                parsed_expr = parser.try_parse_expression()
                bp = {line: parsed_expr}
            else:
                bp = {line: None}
            self.breakpoints[file].update(bp)
            self.message(f"Breakpoint set at line {line}")
            return True, line

    def remove_breakpoint(self, file: str, line: int) -> tuple[bool, int | str]:
        file = os.path.realpath(file)
        if (bps := self.breakpoints.get(file)) is not None:
            if line in bps:
                bps.pop(line)
                self.message(f"Breakpoint removed from line {line}")
                return True, line
                # response = DebuggerResponse(type="breakpoint_removed", body={"lineno": line})
            else:
                msg = f"There is no breakpoint at line {line}"
                self.message(msg)
                return False, msg
                # response = DebuggerResponse(type="bad_request", body={"msg": msg})
        else:
            return False, "Unknown error occurred during removing breakpoint"

    def remove_all_breakpoints(self, file: str) -> tuple[bool, None | str]:
        file = os.path.realpath(file)
        self.breakpoints[file] = {}
        self.message(f"All breakpoints removed.")
        return True, None
