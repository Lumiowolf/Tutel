import atexit
import functools
import io
import os
import sys
import threading
from queue import Queue
from typing import Callable, Type, NamedTuple

from Tutel import debugger
from Tutel.common.ErrorType import InterpreterException, Stop, TutelDebuggerException
from Tutel.common.Utils import mock_debug_callback
from Tutel.core.LexerModule.Lexer import get_bp_possible_lines
from Tutel.debugger import TutelDebugger
from Tutel.debugger.RequestsHandler.Commands import Command
from Tutel.debugger.RequestsHandler.DataStructures import DebuggerResponse, DebuggerEvent, DebuggerRequest, \
    DebuggerResponseType
from Tutel.debugger.RequestsHandler.RequestsHandlerInterface import RequestsHandlerInterface
from Tutel.debugger.RequestsHandler.WebSocketsRequestsHandler import WebSocketsRequestsHandler
from Tutel.debugger.TutelDebugger import StopEvent

HELP = {
    Command.FILE: "f(ile) <filename> - Import Tutel source code.",
    Command.RUN: "r(un) - Start debugging of Tutel code.",
    Command.RUN_UNSTOPPABLE: "run_no_debug - Start execution of Tutel code without debugging.",
    Command.RESTART: "restart - Restart execution of Tutel code from beginning.",
    Command.STOP: "stop - Stop execution of Tutel code.",
    Command.EXIT: "exit - Exit debugger.",
    Command.CONTINUE: "c(ontinue) - Continue execution.",
    Command.STEP_INTO: "step_into - Try to step into function call, step over if not possible.",
    Command.STEP_OVER: "s(tep_over) - Step over to next line in current function or to line where it was called.",
    Command.PAUSE: "pause - Pause program execution.",
    Command.STACK: "stack - Display call stack.",
    Command.FRAME: "frame <number> - Display selected stack frame.",
    Command.BREAK: "b(reak) <file> - Display list of set breakpoints for given file.\n"
                   "b(reak) <file> <number> - Set breakpoint for given file and line.",
    Command.BREAK_EXPRESSION: "break_expr <file> <number> - Set expression breakpoint for given file and line.",
    Command.CLEAR: "clear <file> - Clear all breakpoints for given file.\n"
                   "clear <file> <number> - Remove breakpoint for given file.",
    Command.BP_LINES: "get_bp_lines - Display lines at which breakpoints can be set.",
    Command.HELP: "h(elp) - Display this help message.",
}


class Action(NamedTuple):
    func: Callable
    args: list


def get_help_message():
    header = "Available commands:"
    indent = "\t"
    body = [f"{line.split(' - ')[0]:<25} - {line.split(' - ')[1]:<25}" for line in "\n".join(HELP.values()).splitlines()]
    body = f"\n{indent}".join(body)
    return f"{header}\n\t{body}"


class TutelDebuggerInteractive(TutelDebugger):
    def __init__(self, communication_class: Type[RequestsHandlerInterface], *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tells if the interpreter is running
        self.running = False
        # Tells if the debugger has to terminate
        self.exit = False

        self.request_queue: Queue[tuple[DebuggerRequest, DebuggerResponse]] = Queue()
        self.communication_class = communication_class
        self.communication_class().start(self.request_queue)
        self.emit_event = lambda e: communication_class().emit_event(e)

        self.message_handler = io.StringIO() if communication_class is WebSocketsRequestsHandler else sys.stdout

        self.resume_event = threading.Event()
        atexit.register(self.__exit)

    @property
    @functools.lru_cache(maxsize=128)
    def actions(self) -> dict[Command, Action]:
        cmds = {
            Command.HELP: Action(func=self.help_request, args=[[]]),
            Command.FILE: Action(func=self.file_request, args=[[str]]),
            Command.BP_LINES: Action(func=self.get_bp_lines_request, args=[[]]),
            Command.RUN: Action(func=self.run_request, args=[[]]),
            Command.RUN_UNSTOPPABLE: Action(func=self.run_no_debug_request, args=[[]]),
            Command.RESTART: Action(func=self.restart_request, args=[[]]),
            Command.STOP: Action(func=self.stop_request, args=[[]]),
            Command.EXIT: Action(func=self.exit_request, args=[[]]),
            Command.CONTINUE: Action(func=self.continue_request, args=[[]]),
            Command.STEP_INTO: Action(func=self.step_into_request, args=[[]]),
            Command.STEP_OVER: Action(func=self.step_over_request, args=[[]]),
            Command.PAUSE: Action(func=self.pause_request, args=[[]]),
            Command.STACK: Action(func=self.stack_request, args=[[]]),
            Command.FRAME: Action(func=self.frame_request, args=[[int]]),
            Command.BREAK: Action(func=self.break_request, args=[[str, int], [str]]),
            Command.BREAK_EXPRESSION: Action(func=self.expression_break_request, args=[[str, int, str]]),
            Command.CLEAR: Action(func=self.clear_request, args=[[str, int], [str]]),
        }
        return cmds

    @staticmethod
    def check_action_args(action: Action, request: DebuggerRequest) -> bool:
        return [type(a) for a in request.args] in action.args

    def _clean_up(self):
        super()._clean_up()
        self._stop_session()
        self.exit = False
        self.step_into_mode = False
        self.step_over_mode = False
        if debugger.DEBUGGER_OUT:
            with open(debugger.DEBUGGER_OUT, "w"):
                pass
        self.emit_event(DebuggerEvent(type="end"))

    def _stop_session(self):
        self.running = False
        self.interpreter.stop()
        self.resume_event.set()

    def _post_morten(self, e: InterpreterException):
        super()._post_morten(e)
        self.emit_event(DebuggerEvent(type="post_mortem", description=str(e)))
        self._stop_session()

    def message(self, msg):
        self.message_handler.write(str(msg))
        self.message_handler.write("\n\n")

    def start(self):
        self.message("Type h(help) to see available commands.")
        while not self.exit:
            request, response = self.request_queue.get()
            self.execute_request(request, response)
        self.__exit()
        self.communication_class().join()

    def _break(self, _type: StopEvent):
        super()._break(_type)
        self.emit_event(DebuggerEvent(type=_type.name))

        self.resume_event.clear()
        self.resume_event.wait()

    def check_line(self):
        if not self.running:
            raise Stop
        if not self.interpreter.call_stack:
            return
        if self.pause_mode:
            self.pause_mode = False
            self._break(StopEvent.Pause)
        elif self.step_into_mode and self.interpreter.lineno in self.bp_possible_lines[self.filename]:
            self.step_into_mode = False
            self._break(StopEvent.StepInto)
        elif self.step_over_mode and self.interpreter.curr_frame.index == self.watched_frame:
            self.step_over_mode = False
            self.watched_frame = None
            self._break(StopEvent.StepOver)
        elif self.step_over_mode and self.interpreter.dropped_frame and self.interpreter.dropped_frame.index == self.watched_frame:
            self.step_over_mode = False
            self.watched_frame = None
            self._break(StopEvent.StepOver)
        elif self.interpreter.lineno in self.breakpoints[self.filename]:
            expr = self.breakpoints[self.filename].get(self.interpreter.lineno)
            if expr is None:
                self._break(StopEvent.Breakpoint)
            else:
                # Prevent overwriting current interpreter lineno
                expr.lineno = self.interpreter.lineno
                self.interpreter.lineno_update_enabled = False
                if expr.accept(self.interpreter):
                    self._break(StopEvent.Breakpoint)
                self.interpreter.lineno_update_enabled = True

    def execute_request(self, request: DebuggerRequest, response: DebuggerResponse):
        if request.command == Command.UNKNOWN or request.command not in self.actions:
            self.message(f"Unknown command.")
            request.reject()
            return
        action = self.actions[request.command]
        if not self.check_action_args(action, request):
            self.message(f"Usage:\n{HELP[request.command]}")
            request.reject()
            return
        try:
            action.func(response, *request.args)
        except TutelDebuggerException as e:
            self.message(f"Error: {str(e)}")
            request.reject()
            return

        request.resolve()

    def help_request(self, response: DebuggerResponse):
        self.message(get_help_message())

    def file_request(self, response: DebuggerResponse, path: str):
        path = os.path.realpath(path)
        try:
            with open(path, "r") as file:
                self.code = file.read()
            self.filename = path
            self.bp_possible_lines[self.filename] = get_bp_possible_lines(self.code)
            if self.breakpoints.get(self.filename) is None:
                self.breakpoints[self.filename] = {}
            else:
                bps = self.breakpoints[self.filename]
                new_bps = {}
                for bp in bps:
                    if bp in self.bp_possible_lines.get(self.filename):
                        new_bps[bp] = bps[bp]
                self.breakpoints[self.filename] = new_bps
            response.type = DebuggerResponseType.FILE_SET
            response.body = {"file": path}
        except FileNotFoundError:
            response.type = DebuggerResponseType.BAD_REQUEST
            response.body = {"msg", "File not found."}

    def get_bp_lines_request(self, response: DebuggerResponse):
        self.get_bp_lines()

    def run_request(self, response: DebuggerResponse):
        if not self.running:
            self.interpreter.debug_callback = self.check_line
            self.running = True
            if not self.run():
                self.running = False
            else:
                response.type = DebuggerResponseType.STARTED
        else:
            self.message("Program is already running, use command `restart` to restart it.")

    def run_no_debug_request(self, response: DebuggerResponse):
        if not self.running:
            self.interpreter.debug_callback = mock_debug_callback
            self.running = True
            if not self.run():
                self.running = False
            else:
                response.type = DebuggerResponseType.STARTED
        else:
            self.message("Program is already running, use command `restart` to restart it.")

    def restart_request(self, response: DebuggerResponse):
        if self.running:
            self._clean_up()
            self.message("Restarting program.")
            self.running = True
            self.run()
        else:
            self.message("Program is not running, use command `r(un)` to run it.")

    def stop_request(self, response: DebuggerResponse):
        if self.running:
            self._stop_session()
            self.message("Stopping program. Debugger is still running, use command `exit` to stop it.")
        else:
            self.message("Program is not running, use command `r(un)` to run it.")

    def __exit(self):
        self._stop_session()
        self.emit_event(DebuggerEvent(type="exit"))
        self.communication_class().stop()

    def exit_request(self, response: DebuggerResponse):
        self.exit = True

    def continue_request(self, response: DebuggerResponse):
        if self.running:
            self.resume_event.set()
            response.type = DebuggerResponseType.RESUMED
        else:
            msg = "Program is not running, use command `r(un)` to run it."
            self.message(msg)
            response.type = DebuggerResponseType.BAD_REQUEST
            response.body = {"msg": msg}

    def step_into_request(self, response: DebuggerResponse):
        self.step_into_mode = True
        if self.running:
            self.resume_event.set()
            response.type = DebuggerResponseType.RESUMED
        else:
            self.run_request(response)

    def step_over_request(self, response: DebuggerResponse):
        self.step_over_mode = True
        if self.running:
            self.watched_frame = self.interpreter.curr_frame.index
            self.resume_event.set()
            response.type = DebuggerResponseType.RESUMED
        else:
            self.watched_frame = 0
            self.run_request(response)

    def pause_request(self, response: DebuggerResponse):
        self.pause_mode = True

    def stack_request(self, response: DebuggerResponse):
        success, result = self.stack()
        if success:
            response.type = DebuggerResponseType.STACK
            response.body = {"stack": result}
        else:
            response.type = DebuggerResponseType.BAD_REQUEST
            response.body = {"msg": result}

    def frame_request(self, response: DebuggerResponse, index: int):
        success, result = self.frame(index)
        if success:
            response.type = DebuggerResponseType.FRAME
            response.body = {"frame": result}
        else:
            response.type = DebuggerResponseType.BAD_REQUEST
            response.body = {"msg": result}

    def break_request(self, response: DebuggerResponse, file: str, line: int = None):
        if line is not None:
            success, result = self.set_breakpoint(file, line)
            if success:
                response.type = DebuggerResponseType.BP_SET
                response.body = {"line": line}
        else:
            success, result = self.get_breakpoints(file)
            if success:
                response.type = DebuggerResponseType.BPS
                response.body = {"lines": result}

        if not success:
            response.type = DebuggerResponseType.BAD_REQUEST
            response.body = {"msg": result}

    def expression_break_request(self, response: DebuggerResponse, file: str, line: int, expr: str):
        success, result = self.set_breakpoint(file, line, expr)
        if success:
            response.type = DebuggerResponseType.BP_SET
            response.body = {"line": line}

        if not success:
            response.type = DebuggerResponseType.BAD_REQUEST
            response.body = {"msg": result}

    def clear_request(self, response: DebuggerResponse, file: str, line: int = None):
        if line is not None:
            success, result = self.remove_breakpoint(file, line)
            if success:
                response.type = DebuggerResponseType.BP_CLEARED
                response.body = {"line": result}
        else:
            success, result = self.remove_all_breakpoints(file)
            if success:
                response.type = DebuggerResponseType.ALL_BP_CLEARED

        if not success:
            response.type = DebuggerResponseType.BAD_REQUEST
            response.body = {"msg": result}

