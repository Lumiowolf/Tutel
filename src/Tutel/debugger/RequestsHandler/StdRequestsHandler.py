import sys
from io import StringIO

from Tutel.common.ErrorHandler import ErrorHandler
from Tutel.debugger.RequestsHandler.DataStructures import DebuggerResponse, DebuggerEvent
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
    def __init__(self, error_handler: ErrorHandler = None):
        self.error_handler = error_handler or ErrorHandler(module="debugger")
        self.error_handler.logger.disabled = True
        self.prompt = "> "
        self.input_method = lambda p: StringIO(_input(p))
        self.output_method = lambda r: _output("Debugger response: ", r)

    def receive_request(self):
        raw_request = self.input_method(self.prompt)
        request = RequestParser(RequestLexer(raw_request), error_handler=self.error_handler).parse()
        return request

    def send_response(self, response: DebuggerResponse | DebuggerEvent):
        self.output_method(response.serialize())


if __name__ == '__main__':
    requestHandler = StdRequestsHandler()
    print(requestHandler.receive_request())
