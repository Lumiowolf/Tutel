import atexit
import signal
import sys
import unittest
from time import sleep

from DebuggerTests import test_Debugger
from tests.InterpreterTests import test_Interpreter
from tests.LexerTests import test_Lexer
from tests.ParserTests import test_Parser


def suite():
    suite_ = unittest.TestSuite()
    suite_.addTest(test_Parser.suite())
    suite_.addTest(test_Lexer.suite())
    suite_.addTest(test_Interpreter.suite())
    suite_.addTest(test_Debugger.suite())
    return suite_


def main():
    unittest.main(defaultTest='suite')


def _exit(*args):
    if _exit.alreadyExited:
        return
    _exit.alreadyExited = True
    print("Program terminated.")
    atexit._run_exitfuncs()
    for i in range(0, 3):
        sys.stdout.write(".")
        sys.stdout.flush()
        sleep(1)
    print()
    sys.exit(0)


_exit.alreadyExited = False

if __name__ == '__main__':
    signal.signal(signal.SIGINT, _exit)
    main()
