import os
import sys
import threading
from time import sleep
from typing import Callable

from Tutel import debugger
from Tutel.common.ErrorHandler import ErrorHandler
from Tutel.common.ErrorType import InterpreterException, Stop, TutelException
from Tutel.core.InterpreterModule.Interpreter import Interpreter
from Tutel.core.LexerModule.Lexer import get_bp_possible_lines
from Tutel.core.Runner.TutelRunner import TutelRunner
from Tutel.core.Runner.TutelOptions import TutelOptions
from Tutel.debugger.RequestsHandler.DataStructures import DebuggerResponse, DebuggerEvent
from Tutel.debugger.RequestsHandler.RequestsHandlerInterface import RequestsHandlerInterface

commands = {}


def send_response(msg: str):
    if debugger.DEBUGGER_OUT:
        with open(debugger.DEBUGGER_OUT, "a") as f:
            f.write(msg)
            f.write('\n')
    else:
        sys.stdout.write(msg)
        sys.stdout.write('\n')


class InterpreterThread(threading.Thread):
    def __init__(self, exec_fun: Callable, exec_args: tuple, handle_error: Callable, post_exec: Callable):
        super().__init__()
        self.exec_fun = exec_fun
        self.exec_args = exec_args
        self.handle_error = handle_error
        self.post_exec = post_exec

    def run(self) -> None:
        try:
            self.exec_fun(*self.exec_args)
            self.post_exec()
        except Stop:
            pass
        except InterpreterException as e:
            self.handle_error(e)


class TutelDebugger(TutelRunner):
    def __init__(self, filename: str = None,
                 options: TutelOptions = None,
                 requests_handler: RequestsHandlerInterface = None,
                 error_handler: ErrorHandler = None):
        super().__init__(None, options)
        self.error_handler = error_handler or ErrorHandler(module="debugger")
        self.requests_handler = requests_handler or RequestsHandlerInterface()
        self.bp_possible_lines: dict[str, set[int]] = {}
        self.breakpoints: dict[str, set[int]] = {}
        self.interpreter = Interpreter(debug_callback=self.check_line)
        self.step_mode = False
        self.next_mode = False
        self.watched_frame = None
        self.interactive = False
        self.filename = filename

        if self.filename:
            self.breakpoints[self.filename] = set()
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
        self.step_mode = False
        self.next_mode = False
        self.watched_frame = None
        self.interpreter.clean_up()
        if self.options.gui_out_path:
            with open(self.options.gui_out_path, "a") as file:
                file.write('\n')
                sleep(1)
                file.write('\n')
        self.requests_handler.send_response(DebuggerEvent(event="end"))

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
        self.requests_handler.send_response(DebuggerEvent(event="run"))
        thread.start()

        return True

    def check_line(self):
        if self.step_mode:
            self._break()
        elif self.next_mode and self.interpreter.dropped_frame and self.interpreter.dropped_frame.index == self.watched_frame:
            self._break()
        elif self.interpreter.lineno in self.breakpoints[self.filename]:
            self._break()

    def _break(self):
        _type = "next" if self.next_mode else "step" if self.step_mode else "break"
        self.message(f"Program stopped in function {self.interpreter.curr_frame.name} "
                     f"at line {self.interpreter.curr_frame.lineno}")
        self.requests_handler.send_response(DebuggerEvent(event=_type))

    def _post_morten(self, e: TutelException):
        self.message(f"Program raised exception: '{e}'. Entering post mortem mode.")
        self.requests_handler.send_response(DebuggerEvent(event="post_mortem", description=str(e)))

    def is_source_code_set(self, file: str = None) -> bool:
        file = file or self.filename
        if self.breakpoints.get(file) is not None and self.bp_possible_lines.get(file) is not None:
            return True
        self.message(f"Source code not provided. Use command 'file' to set source code.")
        self.requests_handler.send_response(
            DebuggerResponse(response="bad_request", body={"msg": "Source code not provided."})
        )
        return False

    def get_bp_lines(self):
        if not self.is_source_code_set():
            return
        self.message(f"Breakpoints can be set at lines: {self.bp_possible_lines[self.filename]}")
        self.requests_handler.send_response(
            DebuggerResponse(response="breakpoint_lines",
                             body={"lines": sorted(list(self.bp_possible_lines[self.filename]))})
        )

    def stack(self):
        if not self.is_source_code_set():
            return
        if len(self.interpreter.call_stack) == 0:
            stack = None
            self.message("Stack is empty.")
        else:
            stack = list(reversed(self.interpreter.call_stack))
            if stack:
                for frame in stack:
                    frame.file = self.filename
            self.message(stack)

        self.requests_handler.send_response(
            DebuggerResponse(response="stack_trace", body={"stack": stack}))

    def frame(self, index: int):
        if not self.is_source_code_set():
            return
        if index in range(len(self.interpreter.call_stack)):
            frame = list(reversed(self.interpreter.call_stack))[index]
            self.message(frame)
        else:
            msg = f"Stack index out of range, stack size is {len(self.interpreter.call_stack)}."
            self.message(msg)
            self.requests_handler.send_response(
                DebuggerResponse(response="bad_request", body={"msg": msg}))
            return
        if frame:
            frame.file = self.filename
        self.requests_handler.send_response(
            DebuggerResponse(response="frame", body={"frame": frame}))

    def get_breakpoints(self, file: str):
        file = os.path.realpath(file)
        if (bps := self.breakpoints.get(file)) is not None:
            if len(bps) > 0:
                self.message(f"Breakpoints are set at lines: {list(bps)}.")
            else:
                self.message(f"There are no breakpoints set.")
            response = DebuggerResponse(response="breakpoints", body={"breakpoints": list(bps)})
        else:
            response = DebuggerResponse(response="bad_request",
                                        body={"msg": "Unknown error occurred during setting breakpoint"})
        if response:
            self.requests_handler.send_response(response)

    def set_breakpoint(self, file: str, line: int):
        file = os.path.realpath(file)
        # if not self.is_source_code_set(file):
        #     return
        if self.bp_possible_lines.get(file) is not None and line not in self.bp_possible_lines.get(file):
            msg = f"Could not set breakpoint at line {line}"
            self.message(msg)
            response = DebuggerResponse(response="bad_request", body={"msg": msg})
        else:
            if file not in self.breakpoints:
                self.breakpoints[file] = set()
            self.breakpoints[file].add(line)
            self.message(f"Breakpoint set at line {line}")
            response = DebuggerResponse(response="breakpoint_set", body={"line": line})
        if response:
            self.requests_handler.send_response(response)

    def remove_breakpoint(self, file: str, line: int):
        file = os.path.realpath(file)
        # if not self.is_source_code_set(file):
        #     return
        if (bps := self.breakpoints.get(file)) is not None:
            if line in bps:
                bps.remove(line)
                self.message(f"Breakpoint removed from line {line}")
                response = DebuggerResponse(response="breakpoint_removed", body={"lineno": line})
            else:
                msg = f"There is no breakpoint at line {line}"
                self.message(msg)
                response = DebuggerResponse(response="bad_request", body={"msg": msg})
        else:
            response = DebuggerResponse(response="bad_request",
                                 body={"msg": "Unknown error occurred during removing breakpoint"})
        if response:
            self.requests_handler.send_response(response)

    def remove_all_breakpoints(self, file: str):
        file = os.path.realpath(file)
        self.breakpoints[file] = set()
        self.message(f"All breakpoints removed.")
        self.requests_handler.send_response(
            DebuggerEvent(event="all_breakpoints_removed")
        )
