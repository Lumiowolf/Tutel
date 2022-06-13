import atexit
import signal
import sys
import unittest
from time import sleep
from Tests.ParserTests import test_Parser
from Tests.LexerTests import test_Lexer
from Tests.InterpreterTests import test_Interpreter


def suite():
    suite = unittest.TestSuite()
    suite.addTest(test_Parser.suite())
    suite.addTest(test_Lexer.suite())
    suite.addTest(test_Interpreter.suite())
    return suite


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
