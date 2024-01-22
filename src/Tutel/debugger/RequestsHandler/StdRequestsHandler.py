import sys
import threading
from io import StringIO
from queue import Queue

from Tutel.common.ErrorHandler import ErrorHandler
from Tutel.debugger.RequestsHandler.DataStructures import DebuggerResponse, DebuggerEvent, DebuggerRequest
from Tutel.debugger.RequestsHandler.RequestLexer import RequestLexer
from Tutel.debugger.RequestsHandler.RequestParser import RequestParser
from Tutel.debugger.RequestsHandler.RequestsHandlerInterface import RequestsHandlerInterface


def _input(prompt=""):
    sys.stdout.write(prompt)
    return sys.stdin.readline()


def _output(*args):
    for line in args:
        sys.stdout.write(line)
    sys.stdout.write("\n")


class StdRequestsHandler(RequestsHandlerInterface):
    _init_done = False

    def __init__(self, error_handler: ErrorHandler = None):
        if StdRequestsHandler._init_done:
            return
        self.error_handler = error_handler or ErrorHandler(module="debugger")
        self.error_handler.logger.disabled = True
        self.prompt = "> "
        self.input_method = lambda p: StringIO(_input(p))
        self.output_method = lambda r: _output("Debugger response: ", r)
        self.handler_thread: threading.Thread | None = None
        StdRequestsHandler._init_done = True

    def start(self, request_queue: Queue[tuple[DebuggerRequest, DebuggerResponse]]):
        self.request_queue = request_queue
        self.handler_thread = threading.Thread(target=self.handle_requests)
        self.handler_thread.start()

    def stop(self):
        StdRequestsHandler.running = False

    def join(self):
        self.handler_thread.join()

    def handle_requests(self):
        while StdRequestsHandler.running:
            if raw_request := self.input_method(self.prompt):
                request = RequestParser(RequestLexer(raw_request), error_handler=self.error_handler).parse()
                response = DebuggerResponse()
                self.request_queue.put((request, response))
                request.finished.wait()
                self.output_method(response.serialize())

    def emit_event(self, event: DebuggerEvent):
        self.output_method(event.serialize())
