import json
import sys
import threading
from typing import Callable

import tutelDebugger
from tutel import Tutel, TutelOptions
from tutel.ErrorHandlerModule.ErrorType import InterpreterException, Exit
from tutel.InterpreterModule.Interpreter import Interpreter
from tutel.InterpreterModule.JsonSerializable import JsonSerializable
from tutel.InterpreterModule.TutelDebuggerInterface import TutelDebuggerInterface

commands = {}


def send_response(msg: str):
    if tutelDebugger.DEBUGGER_OUT:
        with open(tutelDebugger.DEBUGGER_OUT, "a") as f:
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
        except Exit:
            pass
        except InterpreterException as e:
            self.handle_error(e)

class TutelDebugger(Tutel, TutelDebuggerInterface):
    def command(*cmds):
        def wrapper(func):
            for cmd in cmds:
                commands.update(**{cmd: func.__name__})

            def inner(self, *args, **kwargs):
                return func(self, *args, **kwargs)

            return inner

        return wrapper

    def __init__(self, code: str, options: TutelOptions = TutelOptions()):
        super().__init__(code, options)
        self.breakpoints = set()
        self.interpreter = Interpreter(debug=True, debugger=self)
        self.bp_possible_lines = self.__get_bp_possible_lines()
        self.step_mode = False
        self.next_mode = False
        self.watched_frame = None
        self.interactive = False
        self.session = None
        self.stopped = False

    # def check_line(self):
    #     if self.interpreter.lineno in self.breakpoints:
    #         print(self.interpreter.lineno)

    def message(self, msg):
        pass

    def start(self):
        self.session = threading.Thread(target=self.run)
        self.session.start()
        self.session.join()

    def _clean_up(self):
        self.step_mode = False
        self.next_mode = False
        self.watched_frame = None
        self.session = None
        self.stopped = False
        self.interpreter.clean_up()

    def __get_bp_possible_lines(self):
        result = set()

        lines = str.splitlines(self.code)
        for i in range(len(lines)):
            if not lines[i].split("#")[0].isspace():
                result.add(i + 1)

        return result

    def run(self):
        # self._clean_up()
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
        while thread.is_alive():
            if self.interpreter.stopped and not self.stopped:
                self.check_line()

    def check_line(self):
        if self.step_mode:
            self._stack_trace()
        elif self.next_mode and self.interpreter.dropped_frame and self.interpreter.dropped_frame.index == self.watched_frame:
            self._stack_trace()
        elif self.interpreter.lineno in self.breakpoints:
            self._stack_trace()
        self.interpreter.stopped = False
        self.stopped = False

    def _stack_trace(self):
        self.stopped = True
        self.message(f"Program stopped in function {self.interpreter.curr_frame.name} "
                     f"at line {self.interpreter.curr_frame.lineno}")
        send_response(json.dumps({"event": "stack_trace", "body": {"stack": self.interpreter.call_stack}},
                      default=lambda o: o.to_json() if isinstance(o, JsonSerializable) else o))

    def _post_morten(self, e: InterpreterException):
        self.message(f"Program raised exception: '{e}'. Entering post mortem mode.")
        send_response(json.dumps({"event": "post_mortem", "body": {"error": str(e)}}))
        self.stopped = True

    def set_breakpoint(self, line: int):
        if line not in self.bp_possible_lines:
            self.message(f"Could not set breakpoint at line {line})")
            send_response(
                json.dumps({"event": "bad_request", "body": {"msg": f"Could not set breakpoint at line {line})"}}))
            return
        if line not in self.breakpoints:
            self.message(f"Breakpoint set at line {line}")
            send_response(json.dumps({"event": "breakpoint_set", "body": {"lineno": line}}))
            self.breakpoints.add(line)

    def remove_breakpoint(self, line: int):
        try:
            self.breakpoints.remove(line)
            self.message(f"Breakpoint removed from line {line}")
            send_response(json.dumps({"event": "breakpoint_remove", "body": {"lineno": line}}))
        except KeyError:
            self.message(f"There is no breakpoint at line {line}")
            send_response(
                json.dumps({"event": "bad_request", "body": {"msg": f"There is no breakpoint at line {line}"}}))
