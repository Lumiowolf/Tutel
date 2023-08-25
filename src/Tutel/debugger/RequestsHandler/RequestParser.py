from Tutel.common.ErrorHandler import ErrorHandler
from Tutel.common.ErrorType import InvalidCommandArgs, CommandNotEndedProperly
from Tutel.debugger.RequestsHandler.Commands import TEXT_TO_COMMAND, Command, ZERO_ARG_COMMANDS
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

    def _check_command(self, command_list: list) -> str | int | None:
        if not self._token_is(RequestTokenType.T_WORD):
            return None
        value = self.lexer.token.value
        if value not in TEXT_TO_COMMAND:
            return None
        command = TEXT_TO_COMMAND[value]
        if command not in command_list:
            return None
        self.lexer.get_next_token()
        return command

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

        if request := self._try_parse_zero_arg_command():
            return request

        if request := self._try_parse_break_clear():
            return request

        if request := self._try_parse_file():
            return request

        if request := self._try_parse_frame():
            return request

        return None

    def _try_parse_zero_arg_command(self) -> DebuggerRequest | None:
        if command := self._check_command(ZERO_ARG_COMMANDS):
            return DebuggerRequest(command=command)

        return None

    def _try_parse_break_clear(self) -> DebuggerRequest | None:
        if (command := self._check_command([Command.CLEAR, Command.BREAK])) is None:
            return None

        if (file := self._check_and_return(RequestTokenType.T_WORD)) is None:
            self.error_handler.handle_error(InvalidCommandArgs(command))

        if (line := self._check_and_return(RequestTokenType.T_NUMBER)) is None:
            return DebuggerRequest(command=command, args=(file,))

        return DebuggerRequest(command=command, args=(file, line))

    def _try_parse_file(self) -> DebuggerRequest | None:
        if (command := self._check_command([Command.FILE])) is None:
            return None

        if (arg := self._check_and_return(RequestTokenType.T_WORD)) is None:
            self.error_handler.handle_error(InvalidCommandArgs(command))

        return DebuggerRequest(command=command, args=(arg,))

    def _try_parse_frame(self) -> DebuggerRequest | None:
        if (command := self._check_command([Command.FRAME])) is None:
            return None

        if (arg := self._check_and_return(RequestTokenType.T_NUMBER)) is None:
            self.error_handler.handle_error(InvalidCommandArgs(command))

        return DebuggerRequest(command=command, args=(arg,))
