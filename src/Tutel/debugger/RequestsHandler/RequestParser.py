from Tutel.common.ErrorHandler import ErrorHandler
from Tutel.common.ErrorType import CommandNotEndedProperly
from Tutel.debugger.RequestsHandler.Commands import TEXT_TO_COMMAND, Command
from Tutel.debugger.RequestsHandler.DataStructures import DebuggerRequest
from Tutel.debugger.RequestsHandler.RequestLexer import RequestLexer, RequestTokenType


class RequestParser:
    def __init__(self, lexer: RequestLexer, error_handler: ErrorHandler = None):
        self.lexer = lexer
        self.lexer.get_next_token()
        self.error_handler = error_handler or ErrorHandler(module="debugger")

    def _check_and_return(self, token_type: RequestTokenType) -> str | int | None:
        if not self._token_is(token_type):
            return None
        value = self.lexer.token.value
        self.lexer.get_next_token()
        return value

    def _check_and_consume(self, token_type: RequestTokenType) -> bool:
        if not self._token_is(token_type):
            return False
        self.lexer.get_next_token()
        return True

    def _token_is(self, token_type: RequestTokenType) -> bool:
        return self.lexer.token.type == token_type

    def parse(self) -> DebuggerRequest:
        if (request := self._parse_request()) is None:
            return DebuggerRequest(command=Command.UNKNOWN)

        if not self._token_is(RequestTokenType.T_ETX):
            self.error_handler.handle_error(CommandNotEndedProperly(command=request.command))

        return request

    def _parse_request(self) -> DebuggerRequest | None:
        request: DebuggerRequest

        if (command := self._try_parse_command()) is None:
            return None

        args = []
        while (arg := self._try_parse_arg()) is not None:
            args.append(arg)

        return DebuggerRequest(command=command, args=tuple(args))

    def _try_parse_command(self) -> Command | None:
        if not self._token_is(RequestTokenType.T_WORD):
            return None

        if (command := TEXT_TO_COMMAND.get(self.lexer.token.value)) is None:
            return None

        self.lexer.get_next_token()
        return command

    def _try_parse_arg(self) -> str | int | None:
        if (arg := self._check_and_return(RequestTokenType.T_WORD)) is not None:
            return arg

        if (arg := self._check_and_return(RequestTokenType.T_NUMBER)) is not None:
            return arg

        if (arg := self._check_and_return(RequestTokenType.T_TEXT_CONST)) is not None:
            return arg

        return None


if __name__ == '__main__':
    from io import StringIO
    parser = RequestParser(RequestLexer(StringIO(input())))
    print(parser.parse())
