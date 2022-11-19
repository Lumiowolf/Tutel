import logging
import unittest
from io import StringIO

from parameterized import parameterized

from tutel.ErrorHandlerModule.ErrorHandler import ErrorHandler
from tutel.ErrorHandlerModule.ErrorType import InterpreterException, NothingToRunException, RecursionException, \
    NotDefinedException, NotIterableException, CannotAssignException, UnsupportedOperandException, \
    BadOperandForUnaryException, AttributeException, MismatchedArgsCountException, OutOfRangeException, TypeException
from tutel.GuiModule.GuiMock import GuiMock
from tutel.InterpreterModule.Interpreter import Interpreter
from tutel.LexerModule.Lexer import Lexer
from tutel.ParserModule.Parser import Parser


def get_error_handler():
    return ErrorHandler(module="test_interpreter", level=logging.CRITICAL)


class TestInterpreter(unittest.TestCase):
    # def setUp(self) -> None:
    #     from tutel.InterpreterModule.Interpreter import set_gui
    #     set_gui(GuiMock(verbose=True))

    @parameterized.expand([
        ("foo(){a = 1;}",),
        ("foo(){a = 1;a += 1;}",),
        ("foo(){a = 1;a -= 1;}",),
        ("foo(){a = 1;a *= 1;}",),
        ("foo(){a = 1;a /= 1;}",),
        ("foo(){a = 1;a %= 1;}",),
        ("foo(){a = 1 + 2;}",),
        ("foo(){a = 1 - 2;}",),
        ("foo(){a = 1 * 2;}",),
        ("foo(){a = 1 / 2;}",),
        ("foo(){a = 1 // 2;}",),
        ("foo(){a = 1 % 2;}",),
        ("foo(){a = -1;}",),
        ("foo(){a = 1;b = -a;}",),
        ("foo(){a = 1;b = a + 1;}",),
        ("foo(){a = 1;b = a - 1;}",),
        ("foo(){a = 1;b = a * 1;}",),
        ("foo(){a = 1;b = a / 1;}",),
        ("foo(){a = 1;b = a // 1;}",),
        ("foo(){a = 1;b = a % 1;}",),
        ("foo(){a = 1;b = 2; c = a + b;}",),
        ("foo(){a = 1;b = 2; c = a - b;}",),
        ("foo(){a = 1;b = 2; c = a * b;}",),
        ("foo(){a = 1;b = 2; c = a / b;}",),
        ("foo(){a = 1;b = 2; c = a // b;}",),
        ("foo(){a = 1;b = 2; c = a % b;}",),
        ("foo(){a = true;}",),
        ("foo(){a = false;}",),
        ("foo(){a = not true;}",),
        ("foo(){a = true and true;}",),
        ("foo(){a = true or true;}",),
        ("foo(){a = false;b = a and true;}",),
        ("foo(){a = false;b = not a;}",),
        ("foo(){a = false;b = true;c = a and b;}",),
        ("foo(){a = false;b = true;c = a or b;}",),
        ("foo(){a = false;b = true;c = a and not b;}",),
        ("foo(){a = false;b = true;c = a or not b;}",),
        ("foo(){a = 1 == 2;}",),
        ("foo(){a = 1 != 2;}",),
        ("foo(){a = 1 > 2;}",),
        ("foo(){a = 1 >= 2;}",),
        ("foo(){a = 1 < 2;}",),
        ("foo(){a = 1 <= 2;}",),
        ("foo(){a = 1;b = a == 2;}",),
        ("foo(){a = 1;b = a != 2;}",),
        ("foo(){a = 1;b = a > 2;}",),
        ("foo(){a = 1;b = a >= 2;}",),
        ("foo(){a = 1;b = a < 2;}",),
        ("foo(){a = 1;b = a <= 2;}",),
        ("foo(){a = 1;b = 2;c = a == b;}",),
        ("foo(){a = 1;b = 2;c = a != b;}",),
        ("foo(){a = 1;b = 2;c = a > b;}",),
        ("foo(){a = 1;b = 2;c = a >= b;}",),
        ("foo(){a = 1;b = 2;c = a < b;}",),
        ("foo(){a = 1;b = 2;c = a <= b;}",),
        ("foo(){a = null;}",),
        ("foo(){a = 'test';}",),
        ("foo(){a = 'test' + '1';}",),
        ("foo(){a = 'test' + '1';}",),
        ("foo(){a = 'test';b = a + '1';}",),
        ("foo(){a = 'test';b = '1';c = a + b;}",),
        ("foo(){a = [];}",),
        ("foo(){a = [1];}",),
        ("foo(){a = [1, 2];}",),
        ("foo(){a = [1, 2];b = 1 in a;}",),
        ("foo(){a = 1 in [1];}",),
        ("foo(){a = [1, 2];a.append(3);}",),
        ("foo(){a = [1, 2];a += [3];}",),
        ("foo(){a = [1, 2];b = [3];c = a + b;}",),
        ("foo(){if(1 > 0){a = 1;}a += 1;}",),
        ("foo(){if(true and true){a = 1;}a += 1;}",),
        ("foo(){if(1 > 1){}elif(true){a = 1;}a += 1;}",),
        ("foo(){if(1 > 2){}elif(false){}else{a = 1;}a += 1;}",),
        ("foo(){a = [1, 2];b = 0;for(el in a){b += 1;}}",),
        ("foo(){a = 0;for(el in [1, 2]){a += 1;}}",),
        ("foo(){a = 3;while(a > 0){a -= 1;}}",),
        ("foo(){while(true){a = 1;return;}}",),
        ("foo(){while(true){if(true){a = 1;return;}}}",),
        ("foo(){while(true){if(false){}elif(true){a = 1;return;}}}",),
        ("foo(){while(true){if(false){}elif(false){}else{a = 1;return;}}}",),
        ("foo(){for(el in [1, 2, 3]){return;}}",),
        ("foo(){sleep(1);}",),
        ("foo(){boo();}boo(){}",),
        ("foo(){x = 1;boo(x);}boo(a){}",),
        ("foo(){x = 1;boo(x);}boo(a){a += 1;}",),
        ("foo(){x = 1;x = boo(x);}boo(a){return a + 1;}",),
        ("foo(){x = 1;x = boo(x);}boo(a){return a + 1, 2;}",),
        ("foo(){a = [1, 2];b = a[0];}",),
        ("foo(){[print][0]('a');}",),
        ("foo(){a = [1, 2][0];}",),
        ("foo(){a = 'abc'[0];}",),
    ])
    def test_basic(self, case):
        # GIVEN
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(error_handler)
        program = parser.parse(lexer)
        interpreter = Interpreter(error_handler)

        # WHEN
        try:
            interpreter.execute(program)

        # THEN
        except InterpreterException as e:
            self.fail(f"Interpreter exception: {e}")

    @parameterized.expand([
        ("foo(){a = Turtle();}",),
        ("foo(){a = Turtle();a.color = Color(0, 0, 255);}",),
        ("foo(){a = Turtle();a.position = Position(20, 20);}",),
        ("foo(){a = Turtle();a.orientation = 45;}",),
        ("foo(){a = Turtle();a.forward(45);}",),
        ("foo(){a = Turtle();a.forward(45);b = Turtle();b.color = Color(255, 0, 0);}",),
        ("foo(){a = Turtle();a.turn_right();}",),
        ("foo(){a = Turtle();a.turn_left();}",),
    ])
    def test_builtins(self, case):
        # GIVEN
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(error_handler)
        program = parser.parse(lexer)
        interpreter = Interpreter(error_handler)

        # WHEN
        try:
            interpreter.execute(program)

        # THEN
        except InterpreterException as e:
            self.fail(f"Interpreter exception: {e}")

    @parameterized.expand([
        ("", NothingToRunException),
        ("foo(){foo();}", RecursionException),
        ("foo(){b = a;}", NotDefinedException),
        ("foo(){a += 1;}", NotDefinedException),
        ("foo(){a = 1;for(el in a){}}", NotIterableException),
        ("foo(){1 + 2 = 3;}", CannotAssignException),
        ("foo(){a = 5; a += [2];}", UnsupportedOperandException),
        ("foo(){a = [1] - 'a';}", UnsupportedOperandException),
        ("foo(){a = -[0];}", BadOperandForUnaryException),
        ("foo(){a = 1;b = a.b;}", AttributeException),
        ("foo(){boo(1);}boo(){}", MismatchedArgsCountException),
        ("foo(){boo();}boo(a){}", MismatchedArgsCountException),
        ("foo(){slee();}", NotDefinedException),
        ("foo(){sleep(1, 2);}", TypeException),
        ("foo(){a = [1, 2]; a[2];}", OutOfRangeException),
    ])
    def test_exceptions(self, case, exception):
        # GIVEN
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(error_handler)
        program = parser.parse(lexer)
        interpreter = Interpreter(error_handler)

        # THEN
        self.assertRaises(exception, lambda _: interpreter.execute(program), f"{exception} not caught.")

    def test_start_with_specific_function(self):
        # GIVEN
        case = "foo(){a += 1;}boo(){}"
        start_with = "boo"
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(error_handler)
        program = parser.parse(lexer)
        interpreter = Interpreter(error_handler)

        # WHEN
        try:
            interpreter.execute(program, start_with)
        # THEN
        except NotDefinedException:
            self.fail("Program started from wrong function.")

    def test_start_with_specific_function_exception(self):
        # GIVEN
        case = "foo(){a += 1;}"
        start_with = "boo"
        exception = NotDefinedException
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(error_handler)
        program = parser.parse(lexer)
        interpreter = Interpreter(error_handler)

        # THEN
        self.assertRaises(exception, lambda _: interpreter.execute(program, start_with), f"{exception} not caught.")


def suite():
    suite_ = unittest.TestSuite()
    suite_.addTest(unittest.makeSuite(TestInterpreter, 'test'))
    return suite_
