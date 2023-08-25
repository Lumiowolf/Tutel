import atexit
import functools
import io
import os
import sys
import threading
from typing import Callable

from Tutel import debugger
from Tutel.common.ErrorType import InterpreterException, Stop, InvalidCommandArgs, \
    TutelDebuggerException, ClientConnectionBroken, CommandNotEndedProperly
from Tutel.common.Utils import mock_debug_callback
from Tutel.core.LexerModule.Lexer import get_bp_possible_lines
from Tutel.debugger import TutelDebugger
from Tutel.debugger.RequestsHandler.Commands import Command
from Tutel.debugger.RequestsHandler.DataStructures import DebuggerResponse, DebuggerEvent
from Tutel.debugger.RequestsHandler.RequestsHandlerInterface import RequestsHandlerInterface
from Tutel.debugger.RequestsHandler.StdRequestsHandler import StdRequestsHandler
from Tutel.debugger.RequestsHandler.WebSocketsRequestsHandler import WebSocketsRequestsHandler

HELP = {
    Command.FILE: "f(ile) filename - Import Tutel source code.",
    Command.RUN: "r(un) - Start debugging of Tutel code.",
    Command.RUN_UNSTOPPABLE: "run_no_debug - Start execution of Tutel code without debugging.",
    Command.RESTART: "restart - Restart execution of Tutel code from beginning.",
    Command.STOP: "stop - Stop execution of Tutel code.",
    Command.EXIT: "exit - Exit debugger.",
    Command.CONTINUE: "c(ontinue) - Continue execution.",
    Command.STEP: "s(tep) - Execute next line.",
    Command.NEXT: "n(ext) - Execute next line of currently executed function.",
    Command.STACK: "stack - Display call stack.",
    Command.FRAME: "frame number - Display selected stack frame.",
    Command.BREAK: "b(reak) file - Display list of set breakpoints for given file.\n"
                   "b(reak) file:number - Set breakpoint for given file.",
    Command.CLEAR: "clear file - Clear all breakpoints for given file.\n"
                   "clear file:number - Remove breakpoint for given file.",
    Command.BP_LINES: "get_bp_lines - Display lines at which breakpoints can be set.",
    Command.HELP: "h(elp) - Display this help message.",
}


def get_help_message():
    header = "Available commands:"
    indent = "\t"
    body = [f"{line.split(' - ')[0]:<20} - {line.split(' - ')[1]:<20}" for line in HELP.values()]
    body = f"\n{indent}".join(body)
    return f"{header}\n\t{body}"


class TutelDebuggerInteractive(TutelDebugger):
    def __init__(self, requests_handler: RequestsHandlerInterface = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.running = False
        self.stopped = False
        self.exit = False
        # self.message_handler = StringIO().write if requests_handler else sys.stdout.write
        self.message_handler = io.StringIO() if isinstance(requests_handler, WebSocketsRequestsHandler) else sys.stdout
        self.requests_handler: RequestsHandlerInterface = requests_handler or StdRequestsHandler(
            error_handler=self.error_handler)
        self.stop_event = threading.Event()
        self.resume_event = threading.Event()
        atexit.register(self.do_exit)

    @property
    @functools.lru_cache(maxsize=128)
    def commands(self) -> dict[Command, Callable]:
        cmds = {
            Command.HELP: self.do_help,
            Command.FILE: self.do_file,
            Command.BP_LINES: self.do_get_bp_lines,
            Command.RUN: self.do_run,
            Command.RUN_UNSTOPPABLE: self.do_run_no_debug,
            Command.RESTART: self.do_restart,
            Command.STOP: self.do_stop,
            Command.EXIT: self.do_exit,
            Command.CONTINUE: self.do_continue,
            Command.STEP: self.do_step,
            Command.NEXT: self.do_next,
            Command.STACK: self.do_stack,
            Command.FRAME: self.do_frame,
            Command.BREAK: self.do_break,
            Command.CLEAR: self.do_clear,
        }
        return cmds

    def _clean_up(self):
        super()._clean_up()
        self._stop_session()
        self.exit = False
        self.step_mode = False
        self.next_mode = False
        if debugger.DEBUGGER_OUT:
            with open(debugger.DEBUGGER_OUT, "w"):
                pass
        self.stop_event.set()

    def _stop_session(self):
        self.running = False
        self.stopped = False
        self.resume_event.set()
        self.stop_event.set()
        self.interpreter.clean_up()

    def _post_morten(self, e: InterpreterException):
        super()._post_morten(e)
        self._stop_session()

    def message(self, msg):
        self.message_handler.write(str(msg))
        self.message_handler.write("\n\n")

    def start(self):
        self.message("Type h(help) to see available commands.")
        while not self.exit:
            if self.stopped or not self.running:
                self._do_command()
                if not self.stopped and self.running:
                    self.stop_event.clear()
                    self.stop_event.wait()

    def check_line(self):
        if not self.interpreter.call_stack:
            return
        if self.step_mode and self.interpreter.lineno in self.bp_possible_lines[self.filename]:
            self._break()
        elif self.next_mode and self.interpreter.curr_frame.index == self.watched_frame:
            self._break()
        elif self.next_mode and self.interpreter.dropped_frame and self.interpreter.dropped_frame.index == self.watched_frame:
            self._break()
        elif self.interpreter.lineno in self.breakpoints[self.filename]:
            self._break()
        if not self.running:
            raise Stop

    def _break(self):
        super()._break()
        self.stopped = True
        self.stop_event.set()
        self.resume_event.clear()
        self.resume_event.wait()

    def _do_command(self):
        request = None
        while request is None or request.command not in self.commands:
            try:
                request = self.requests_handler.receive_request()
                if request.command == Command.UNKNOWN or request.command not in self.commands:
                    self.message(f"Unknown command.")
            except (InvalidCommandArgs, CommandNotEndedProperly) as e:
                self.message(f"Usage: {HELP[e.command]}")
        try:
            self.commands[request.command](*request.args)
        except TutelDebuggerException as e:
            self.message(f"Error: {str(e)}")

    def do_help(self):
        self.message(get_help_message())

    def do_file(self, path: str):
        self.filename = os.path.realpath(path)
        try:
            with open(self.filename, "r") as file:
                self.code = file.read()
            self.bp_possible_lines[self.filename] = get_bp_possible_lines(self.code)
            if self.breakpoints.get(self.filename) is None:
                self.breakpoints[self.filename] = set()
            else:
                bps = self.breakpoints[self.filename]
                new_bps = set()
                for bp in bps:
                    if bp in self.bp_possible_lines.get(self.filename):
                        new_bps.add(bp)
                self.breakpoints[self.filename] = new_bps
            self.requests_handler.send_response(DebuggerResponse(response="file_set", body={"file": path}))
        except FileNotFoundError:
            self.error_handler.handle_error(ClientConnectionBroken(self.filename))

    def do_get_bp_lines(self):
        self.get_bp_lines()

    def do_run(self):
        if not self.running:
            self.interpreter.debug_callback = self.check_line
            self.running = True
            if not self.run():
                self.running = False
        else:
            self.message("Program is already running, use command `restart` to restart it.")

    def do_run_no_debug(self):
        if not self.running:
            self.interpreter.debug_callback = mock_debug_callback
            self.running = True
            if not self.run():
                self.running = False
        else:
            self.message("Program is already running, use command `restart` to restart it.")

    def do_restart(self):
        if self.running:
            self._clean_up()
            self.message("Restarting program.")
            self.running = True
            self.run()
        else:
            self.message("Program is not running, use command `r(un)` to run it.")

    def do_stop(self):
        if self.running:
            self._stop_session()
            self.message("Stopping program. Debugger is still running, use command `exit` to stop it.")
        else:
            self.message("Program is not running, use command `r(un)` to run it.")

    def do_exit(self):
        self._stop_session()
        self.exit = True
        self.requests_handler.stop()

    def do_continue(self):
        self.step_mode = False
        self.next_mode = False
        self.watched_frame = None
        if self.running:
            self.stopped = False
            self.resume_event.set()
            self.requests_handler.send_response(DebuggerEvent(event="continue"))
        else:
            self.message("Program is not running, use command `r(un)` to run it.")

    def do_step(self):
        self.next_mode = False
        self.step_mode = True
        if self.running:
            self.stopped = False
            self.resume_event.set()
        else:
            self.do_run()

    def do_next(self):
        self.step_mode = False
        self.next_mode = True
        if self.running:
            self.watched_frame = self.interpreter.curr_frame.index
            self.stopped = False
            self.resume_event.set()
        else:
            self.watched_frame = 0
            self.do_run()

    def do_stack(self):
        self.stack()

    def do_frame(self, index: int):
        self.frame(index)

    def do_break(self, file: str, line: int = None):
        if line is not None:
            self.set_breakpoint(file, line)
        else:
            self.get_breakpoints(file)

    def do_clear(self, file: str, line: int = None):
        if line is not None:
            self.remove_breakpoint(file, line)
        else:
            self.remove_all_breakpoints(file)
