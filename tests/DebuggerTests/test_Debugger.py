import io
import logging
import sys
import unittest
from io import StringIO

from parameterized import parameterized

from Tutel import debugger
from Tutel.common.ErrorHandler import ErrorHandler
from Tutel.common.ErrorType import TutelDebuggerException, CommandNotEndedProperly, InvalidCommandArgs
from Tutel.debugger.RequestsHandler.Commands import Command
from Tutel.debugger.RequestsHandler.DataStructures import DebuggerRequest
from Tutel.debugger.RequestsHandler.RequestLexer import RequestLexer
from Tutel.debugger.RequestsHandler.RequestParser import RequestParser
from Tutel.debugger.TutelDebuggerInteractive import TutelDebuggerInteractive


def get_error_handler():
    return ErrorHandler(module="test_interpreter", level=logging.CRITICAL)


class TestRequestParser(unittest.TestCase):

    @parameterized.expand([
        # Commands without args
        ("h", DebuggerRequest(command=Command.HELP)),
        ("help", DebuggerRequest(command=Command.HELP)),
        ("r", DebuggerRequest(command=Command.RUN)),
        ("run", DebuggerRequest(command=Command.RUN)),
        ("run_no_debug", DebuggerRequest(command=Command.RUN_UNSTOPPABLE)),
        ("restart", DebuggerRequest(command=Command.RESTART)),
        ("stop", DebuggerRequest(command=Command.STOP)),
        ("exit", DebuggerRequest(command=Command.EXIT)),
        ("c", DebuggerRequest(command=Command.CONTINUE)),
        ("continue", DebuggerRequest(command=Command.CONTINUE)),
        ("s", DebuggerRequest(command=Command.STEP)),
        ("step", DebuggerRequest(command=Command.STEP)),
        ("n", DebuggerRequest(command=Command.NEXT)),
        ("next", DebuggerRequest(command=Command.NEXT)),
        ("stack", DebuggerRequest(command=Command.STACK)),
        ("b", DebuggerRequest(command=Command.BREAK)),
        ("break", DebuggerRequest(command=Command.BREAK)),
        ("clear", DebuggerRequest(command=Command.CLEAR)),
        ("get_bp_lines", DebuggerRequest(command=Command.BP_LINES)),
        # Commands with args
        ("b 1", DebuggerRequest(command=Command.BREAK, args=(1,))),
        ("break 1", DebuggerRequest(command=Command.BREAK, args=(1,))),
        ("clear 1", DebuggerRequest(command=Command.CLEAR, args=(1,))),
        ("f dev/test.tut", DebuggerRequest(command=Command.FILE, args=("dev/test.tut",))),
        ("file dev/test.tut", DebuggerRequest(command=Command.FILE, args=("dev/test.tut",))),
        ("frame 0", DebuggerRequest(command=Command.FRAME, args=(0,))),
    ])
    def test_correct(self, case: str, expected: DebuggerRequest):
        # GIVEN
        error_handler = get_error_handler()
        lexer = RequestLexer(StringIO(case))
        parser = RequestParser(lexer, error_handler)

        # WHEN
        request = parser.parse()

        # THEN
        self.assertEqual(request, expected)

    @parameterized.expand([
        # Commands without args
        ("h 1",), ("h a",),
        ("help 1",), ("help a",),
        ("r 1",), ("r a",),
        ("run 1",), ("run a",),
        ("run_no_debug 1",), ("run_no_debug a",),
        ("restart 1",), ("restart a",),
        ("stop 1",), ("stop a",),
        ("exit 1",), ("exit a",),
        ("c 1",), ("c a",),
        ("continue 1",), ("continue a",),
        ("s 1",), ("s a",),
        ("step 1",), ("step a",),
        ("n 1",), ("n a",),
        ("next 1",), ("next a",),
        ("stack 1",), ("stack a",),
        ("get_bp_lines 1",), ("get_bp_lines a",),
        # Commands with args
        ("b 1 1",), ("b a",),
        ("break 1 1",), ("break a",),
        ("clear 1 1",), ("clear a",),
        ("f dev/test.tut a",),
        ("file dev/test.tut a",),
        ("frame 0 1",),
    ])
    def test_redundant_args(self, case: str):
        # GIVEN
        error_handler = get_error_handler()
        lexer = RequestLexer(StringIO(case))
        parser = RequestParser(lexer, error_handler)

        # THEN
        self.assertRaises(CommandNotEndedProperly, parser.parse)

    @parameterized.expand([
        ("f 1",),
        ("file 1",),
        ("frame a",),
    ])
    def test_invalid_args(self, case: str):
        # GIVEN
        error_handler = get_error_handler()
        lexer = RequestLexer(StringIO(case))
        parser = RequestParser(lexer, error_handler)

        # THEN
        self.assertRaises(InvalidCommandArgs, parser.parse)

    @parameterized.expand([
        ("f",),
        ("file",),
        ("frame",),
    ])
    def test_missing_args(self, case: str):
        # GIVEN
        error_handler = get_error_handler()
        lexer = RequestLexer(StringIO(case))
        parser = RequestParser(lexer, error_handler)

        # THEN
        self.assertRaises(InvalidCommandArgs, parser.parse)

    @parameterized.expand([
        ("test",),
        ("1232314",),
        ("t",),
        ("1",),
        ("",),
        ("          ",),
    ])
    def test_unknown_command(self, case: str):
        # GIVEN
        error_handler = get_error_handler()
        lexer = RequestLexer(StringIO(case))
        parser = RequestParser(lexer, error_handler)

        # WHEN
        request = parser.parse()

        # THEN
        self.assertEqual(request, DebuggerRequest(Command.UNKNOWN))


class TestDebugger(unittest.TestCase):
    def setUp(self) -> None:
        self._stdin = sys.stdin
        self._stdout = sys.stdout
        sys.stdin = io.StringIO()
        sys.stdout = io.StringIO()

    def tearDown(self) -> None:
        sys.stdin = self._stdin
        sys.stdout = self._stdout

    def test_1(self):
        # GIVEN
        code = """main() {
            a = 1;
        }
        """
        error_handler = get_error_handler()
        debugger = TutelDebuggerInteractive(code=code, error_handler=error_handler)

        # WHEN
        try:
            sys.stdin.write("run\n")
            sys.stdin.write("exit\n")
            sys.stdin.seek(0)
            debugger.start()
        # THEN
        except Exception as e:
            self.fail(f"Debugger exception: {e}")

    def test_2(self):
        # GIVEN
        code = """main() {
            a = 1;
        }
        """
        error_handler = get_error_handler()
        debugger = TutelDebuggerInteractive(code=code, error_handler=error_handler)

        # WHEN
        try:
            sys.stdin.write("break 2\n")
            sys.stdin.write("run\n")
            sys.stdin.write("continue\n")
            sys.stdin.write("exit\n")
            sys.stdin.seek(0)
            debugger.start()
        # THEN
        except Exception as e:
            self.fail(f"Debugger exception: {e}")

    def test_3(self):
        # GIVEN
        code = """main() {
            a = 1;
        }
        """
        error_handler = get_error_handler()
        debugger = TutelDebuggerInteractive(code=code, error_handler=error_handler)

        # WHEN
        try:
            sys.stdin.write("break 2\n")
            sys.stdin.write("run\n")
            sys.stdin.write("continue\n")
            sys.stdin.write("exit\n")
            sys.stdin.seek(0)
            debugger.start()
        # THEN
        except Exception as e:
            self.fail(f"Debugger exception: {e}")


def suite():
    suite_ = unittest.TestSuite()
    suite_.addTest(unittest.makeSuite(TestRequestParser, 'test'))
    suite_.addTest(unittest.makeSuite(TestDebugger, 'test'))
    return suite_
