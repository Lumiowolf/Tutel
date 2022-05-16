import unittest
from io import StringIO

from parameterized import parameterized

from ErrorHandlerModule.ErrorHandler import ErrorHandler
from LexerModule.Lexer import Lexer
from ParserModule.Parser import Parser
from ParserModule.Program import Program, Function, Identifier, BasicAssignment, Integer, AddAssignment, SubAssignment, \
    MulAssignment, DivAssignment, ModAssignment, ReturnStatement, AddExpr, SubExpr, IfStatement, GreaterExpr, ElifBlock, \
    AndExpr, OrExpr, ElseBlock, FunCall, ForStatement, WhileStatement, MulExpr, NegateExpression, EqExpr, NotEqExpr, \
    LessExpr, GreaterEqExpr, LessEqExpr, InExpr, DivExpr, ModExpr, IntDivExpr, DotOperator, ListElement, List, String, \
    BoolTrue, BoolFalse, Null


class TestParser(unittest.TestCase):
    @parameterized.expand([
        ("foo(){}", Program({"foo": Function([], [])})),
        ("foo(){} boo(){}", Program({"foo": Function([], []), "boo": Function([], [])})),
    ])
    def test_try_parse_function_def(self, case, expect):
        # GIVEN
        error_handler = ErrorHandler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(lexer, error_handler)

        # WHEN
        program = parser.parse()

        # THEN
        self.assertEqual(expect, program, f"Function not parsed: {case}")

    @parameterized.expand([
        ("foo(a, b){} boo(a){}",
         Program({"foo": Function([Identifier("a"), Identifier("b")], []), "boo": Function([Identifier("a")], [])})),
        ("foo(a, b, c){} boo(){} bar(var){}",
         Program({"foo": Function([Identifier("a"), Identifier("b"), Identifier("c")], []), "boo": Function([], []),
                  "bar": Function([Identifier("var")], [])})),
    ])
    def test_try_parse_params_list(self, case, expect):
        # GIVEN
        error_handler = ErrorHandler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(lexer, error_handler)

        # WHEN
        program = parser.parse()

        # THEN
        self.assertEqual(expect, program, f"Function params not parsed: {case}")

    @parameterized.expand([
        ("foo(){var = 5;}",
         Program({"foo": Function([], [BasicAssignment(Identifier("var"), Integer(5))])})),
        ("foo(){var = var1;} boo(){var = var1; var2 = var3;}",
         Program({"foo": Function([], [BasicAssignment(Identifier("var"), Identifier("var1"))]), "boo": Function([], [
             BasicAssignment(Identifier("var"), Identifier("var1")),
             BasicAssignment(Identifier("var2"), Identifier("var3"))])})),
    ])
    def test_try_parse_block(self, case, expect):
        # GIVEN
        error_handler = ErrorHandler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(lexer, error_handler)

        # WHEN
        program = parser.parse()

        # THEN
        self.assertEqual(expect, program, f"Function block not parsed: {case}")

    @parameterized.expand([
        ("foo(){var = 5;}",
         Program({"foo": Function([], [BasicAssignment(Identifier("var"), Integer(5))])})),
        ("foo(){var += 5;}",
         Program({"foo": Function([], [AddAssignment(Identifier("var"), Integer(5))])})),
        ("foo(){var -= 5;}",
         Program({"foo": Function([], [SubAssignment(Identifier("var"), Integer(5))])})),
        ("foo(){var *= 5;}",
         Program({"foo": Function([], [MulAssignment(Identifier("var"), Integer(5))])})),
        ("foo(){var /= 5;}",
         Program({"foo": Function([], [DivAssignment(Identifier("var"), Integer(5))])})),
        ("foo(){var %= 5;}",
         Program({"foo": Function([], [ModAssignment(Identifier("var"), Integer(5))])})),
    ])
    def test_try_parse_assignment(self, case, expect):
        # GIVEN
        error_handler = ErrorHandler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(lexer, error_handler)

        # WHEN
        program = parser.parse()

        # THEN
        self.assertEqual(expect, program, f"Assignment not parsed: {case}")

    @parameterized.expand([
        ("foo(){return a;}",
         Program({"foo": Function([], [ReturnStatement([Identifier("a")])])})),
        ("foo(){return a, b;}",
         Program({"foo": Function([], [ReturnStatement([Identifier("a"), Identifier("b")])])})),
        ("foo(){return a, b + c - 2;}",
         Program({"foo": Function([], [
             ReturnStatement([Identifier("a"), SubExpr(AddExpr(Identifier("b"), Identifier("c")), Integer(2))])])})),
    ])
    def test_try_parse_return_statement(self, case, expect):
        # GIVEN
        error_handler = ErrorHandler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(lexer, error_handler)

        # WHEN
        program = parser.parse()

        # THEN
        self.assertEqual(expect, program, f"Return statement not parsed: {case}")

    @parameterized.expand([
        ("foo(){if(a > b){a += 1;}}",
         Program({"foo": Function([], [
             IfStatement(GreaterExpr(Identifier("a"), Identifier("b")), [AddAssignment(Identifier("a"), Integer(1))],
                         [], None)])})),
    ])
    def test_try_parse_if_statement(self, case, expect):
        # GIVEN
        error_handler = ErrorHandler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(lexer, error_handler)

        # WHEN
        program = parser.parse()

        # THEN
        self.assertEqual(expect, program, f"If statement not parsed: {case}")

    @parameterized.expand([
        ("foo(){if(a > b){a += 1;} elif(c and d){e += 1;}}",
         Program({"foo": Function([], [
             IfStatement(GreaterExpr(Identifier("a"), Identifier("b")), [AddAssignment(Identifier("a"), Integer(1))],
                         [ElifBlock(AndExpr(Identifier("c"), Identifier("d")),
                                    [AddAssignment(Identifier("e"), Integer(1))])], None)])})),
        ("foo(){if(a > b){a += 1;} elif(c and d){e += 1;} elif(d or f){e = 1;}}",
         Program({"foo": Function([], [
             IfStatement(GreaterExpr(Identifier("a"), Identifier("b")), [AddAssignment(Identifier("a"), Integer(1))],
                         [ElifBlock(AndExpr(Identifier("c"), Identifier("d")),
                                    [AddAssignment(Identifier("e"), Integer(1))]),
                          ElifBlock(OrExpr(Identifier("d"), Identifier("f")),
                                    [BasicAssignment(Identifier("e"), Integer(1))])], None)])})),
        ("foo(){if(a > b){a += 1;} elif(c and d){e += 1;} elif(d or f){e = 1;} else{print(a);}}",
         Program({"foo": Function([], [
             IfStatement(GreaterExpr(Identifier("a"), Identifier("b")), [AddAssignment(Identifier("a"), Integer(1))],
                         [ElifBlock(AndExpr(Identifier("c"), Identifier("d")),
                                    [AddAssignment(Identifier("e"), Integer(1))]),
                          ElifBlock(OrExpr(Identifier("d"), Identifier("f")),
                                    [BasicAssignment(Identifier("e"), Integer(1))])],
                         ElseBlock([FunCall(Identifier("print"), [Identifier("a")])]))])})),
    ])
    def test_try_parse_elif_block(self, case, expect):
        # GIVEN
        error_handler = ErrorHandler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(lexer, error_handler)

        # WHEN
        program = parser.parse()

        # THEN
        self.assertEqual(expect, program, f"Elif statement not parsed: {case}")

    @parameterized.expand([
        ("foo(){if(a > b){a += 1;} else{print(a);}}",
         Program({"foo": Function([], [
             IfStatement(GreaterExpr(Identifier("a"), Identifier("b")), [AddAssignment(Identifier("a"), Integer(1))],
                         [],
                         ElseBlock([FunCall(Identifier("print"), [Identifier("a")])]))])})),
        ("foo(){if(a > b){a += 1;} elif(c and d){e += 1;} elif(d or f){e = 1;} else{print(a);}}",
         Program({"foo": Function([], [
             IfStatement(GreaterExpr(Identifier("a"), Identifier("b")), [AddAssignment(Identifier("a"), Integer(1))],
                         [ElifBlock(AndExpr(Identifier("c"), Identifier("d")),
                                    [AddAssignment(Identifier("e"), Integer(1))]),
                          ElifBlock(OrExpr(Identifier("d"), Identifier("f")),
                                    [BasicAssignment(Identifier("e"), Integer(1))])],
                         ElseBlock([FunCall(Identifier("print"), [Identifier("a")])]))])})),
    ])
    def test_try_parse_else_block(self, case, expect):
        # GIVEN
        error_handler = ErrorHandler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(lexer, error_handler)

        # WHEN
        program = parser.parse()

        # THEN
        self.assertEqual(expect, program, f"Else statement not parsed: {case}")

    @parameterized.expand([
        ("foo(){for(a in b){print(a);}}",
         Program({"foo": Function([], [
             ForStatement(Identifier("a"), Identifier("b"), [FunCall(Identifier("print"), [Identifier("a")])])])})),
    ])
    def test_try_parse_for_statement(self, case, expect):
        # GIVEN
        error_handler = ErrorHandler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(lexer, error_handler)

        # WHEN
        program = parser.parse()

        # THEN
        self.assertEqual(expect, program, f"For statement not parsed: {case}")

    @parameterized.expand([
        ("foo(){while(a and b){print(a);}}",
         Program({"foo": Function([], [
             WhileStatement(AndExpr(Identifier("a"), Identifier("b")),
                            [FunCall(Identifier("print"), [Identifier("a")])])])})),
    ])
    def test_try_parse_while_statement(self, case, expect):
        # GIVEN
        error_handler = ErrorHandler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(lexer, error_handler)

        # WHEN
        program = parser.parse()

        # THEN
        self.assertEqual(expect, program, f"While statement not parsed: {case}")

    @parameterized.expand([
        ("foo(){a = a and b or c - 2 * 3 and not g;}",
         Program({"foo": Function([], [BasicAssignment(Identifier("a"),
                                                       OrExpr(AndExpr(Identifier("a"), Identifier("b")), AndExpr(
                                                           SubExpr(Identifier("c"), MulExpr(Integer(2), Integer(3))),
                                                           NegateExpression(Identifier("g")))))])})),
    ])
    def test_try_parse_expression(self, case, expect):
        # GIVEN
        error_handler = ErrorHandler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(lexer, error_handler)

        # WHEN
        program = parser.parse()

        # THEN
        self.assertEqual(expect, program, f"Expression not parsed: {case}")

    @parameterized.expand([
        ("foo(){a = c or b;}",
         Program({"foo": Function([], [BasicAssignment(Identifier("a"), OrExpr(Identifier("c"), Identifier("b")))])})),
    ])
    def test_try_parse_or_expr(self, case, expect):
        # GIVEN
        error_handler = ErrorHandler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(lexer, error_handler)

        # WHEN
        program = parser.parse()

        # THEN
        self.assertEqual(expect, program, f"Or expression not parsed: {case}")

    @parameterized.expand([
        ("foo(){a = c and b;}",
         Program({"foo": Function([], [BasicAssignment(Identifier("a"), AndExpr(Identifier("c"), Identifier("b")))])})),
    ])
    def test_try_parse_and_expr(self, case, expect):
        # GIVEN
        error_handler = ErrorHandler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(lexer, error_handler)

        # WHEN
        program = parser.parse()

        # THEN
        self.assertEqual(expect, program, f"And expression not parsed: {case}")

    @parameterized.expand([
        ("foo(){a = not b;}",
         Program({"foo": Function([], [BasicAssignment(Identifier("a"), NegateExpression(Identifier("b")))])})),
    ])
    def test_try_parse_negate_expr(self, case, expect):
        # GIVEN
        error_handler = ErrorHandler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(lexer, error_handler)

        # WHEN
        program = parser.parse()

        # THEN
        self.assertEqual(expect, program, f"Negate expression not parsed: {case}")

    @parameterized.expand([
        ("foo(){a = b == c;}",
         Program({"foo": Function([], [BasicAssignment(Identifier("a"), EqExpr(Identifier("b"), Identifier("c")))])})),
        ("foo(){a = b != c;}",
         Program(
             {"foo": Function([], [BasicAssignment(Identifier("a"), NotEqExpr(Identifier("b"), Identifier("c")))])})),
        ("foo(){a = b > c;}",
         Program(
             {"foo": Function([], [BasicAssignment(Identifier("a"), GreaterExpr(Identifier("b"), Identifier("c")))])})),
        ("foo(){a = b < c;}",
         Program(
             {"foo": Function([], [BasicAssignment(Identifier("a"), LessExpr(Identifier("b"), Identifier("c")))])})),
        ("foo(){a = b >= c;}",
         Program({"foo": Function([], [
             BasicAssignment(Identifier("a"), GreaterEqExpr(Identifier("b"), Identifier("c")))])})),
        ("foo(){a = b <= c;}",
         Program(
             {"foo": Function([], [BasicAssignment(Identifier("a"), LessEqExpr(Identifier("b"), Identifier("c")))])})),
        ("foo(){a = b in c;}",
         Program({"foo": Function([], [BasicAssignment(Identifier("a"), InExpr(Identifier("b"), Identifier("c")))])})),
    ])
    def test_try_parse_comp_expr(self, case, expect):
        # GIVEN
        error_handler = ErrorHandler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(lexer, error_handler)

        # WHEN
        program = parser.parse()

        # THEN
        self.assertEqual(expect, program, f"Comp expression not parsed: {case}")

    @parameterized.expand([
        ("foo(){a = b + c;}",
         Program({"foo": Function([], [BasicAssignment(Identifier("a"), AddExpr(Identifier("b"), Identifier("c")))])})),
        ("foo(){a = b - c;}",
         Program({"foo": Function([], [BasicAssignment(Identifier("a"), SubExpr(Identifier("b"), Identifier("c")))])})),
        ("foo(){a = b + c - d;}",
         Program({"foo": Function([], [
             BasicAssignment(Identifier("a"), SubExpr(AddExpr(Identifier("b"), Identifier("c")), Identifier("d")))])})),
    ])
    def test_try_parse_sum_expr(self, case, expect):
        # GIVEN
        error_handler = ErrorHandler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(lexer, error_handler)

        # WHEN
        program = parser.parse()

        # THEN
        self.assertEqual(expect, program, f"Sum expression not parsed: {case}")

    @parameterized.expand([
        ("foo(){a = b * c;}",
         Program({"foo": Function([], [BasicAssignment(Identifier("a"), MulExpr(Identifier("b"), Identifier("c")))])})),
        ("foo(){a = b / c;}",
         Program({"foo": Function([], [BasicAssignment(Identifier("a"), DivExpr(Identifier("b"), Identifier("c")))])})),
        ("foo(){a = b % c;}",
         Program({"foo": Function([], [BasicAssignment(Identifier("a"), ModExpr(Identifier("b"), Identifier("c")))])})),
        ("foo(){a = b // c;}",
         Program(
             {"foo": Function([], [BasicAssignment(Identifier("a"), IntDivExpr(Identifier("b"), Identifier("c")))])})),
    ])
    def test_try_parse_mul_expr(self, case, expect):
        # GIVEN
        error_handler = ErrorHandler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(lexer, error_handler)

        # WHEN
        program = parser.parse()

        # THEN
        self.assertEqual(expect, program, f"Mul expression not parsed: {case}")

    @parameterized.expand([
        ("foo(){a = b.c;}",
         Program(
             {"foo": Function([], [BasicAssignment(Identifier("a"), DotOperator(Identifier("b"), Identifier("c")))])})),
    ])
    def test_try_parse_dot_operator(self, case, expect):
        # GIVEN
        error_handler = ErrorHandler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(lexer, error_handler)

        # WHEN
        program = parser.parse()

        # THEN
        self.assertEqual(expect, program, f"Dot operator not parsed: {case}")

    @parameterized.expand([
        ("foo(){a = b();}",
         Program({"foo": Function([], [BasicAssignment(Identifier("a"), FunCall(Identifier("b"), []))])})),
    ])
    def test_try_parse_fun_call(self, case, expect):
        # GIVEN
        error_handler = ErrorHandler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(lexer, error_handler)

        # WHEN
        program = parser.parse()

        # THEN
        self.assertEqual(expect, program, f"Function call not parsed: {case}")

    @parameterized.expand([
        ("foo(){a = b(a, b, 5);}",
         Program({"foo": Function([], [BasicAssignment(Identifier("a"), FunCall(Identifier("b"),
                                                                                [Identifier("a"), Identifier("b"),
                                                                                 Integer(5)]))])})),
    ])
    def test_try_parse_arguments(self, case, expect):
        # GIVEN
        error_handler = ErrorHandler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(lexer, error_handler)

        # WHEN
        program = parser.parse()

        # THEN
        self.assertEqual(expect, program, f"Function arguments not parsed: {case}")

    @parameterized.expand([
        ("foo(){a = b[1];}",
         Program({"foo": Function([], [BasicAssignment(Identifier("a"), ListElement(Identifier("b"), Integer(1)))])})),
    ])
    def test_try_parse_list_element(self, case, expect):
        # GIVEN
        error_handler = ErrorHandler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(lexer, error_handler)

        # WHEN
        program = parser.parse()

        # THEN
        self.assertEqual(expect, program, f"List element not parsed: {case}")

    @parameterized.expand([
        ("foo(){a = (a - 5) * 2;}",
         Program({"foo": Function([], [
             BasicAssignment(Identifier("a"), MulExpr(SubExpr(Identifier("a"), Integer(5)), Integer(2)))])})),
    ])
    def test_try_parse_parenthesis(self, case, expect):
        # GIVEN
        error_handler = ErrorHandler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(lexer, error_handler)

        # WHEN
        program = parser.parse()

        # THEN
        self.assertEqual(expect, program, f"List element not parsed: {case}")

    @parameterized.expand([
        ("foo(){a = [1, 2, 3];}",
         Program({"foo": Function([], [
             BasicAssignment(Identifier("a"), List([Integer(1), Integer(2), Integer(3)]))])})),
    ])
    def test_try_parse_list(self, case, expect):
        # GIVEN
        error_handler = ErrorHandler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(lexer, error_handler)

        # WHEN
        program = parser.parse()

        # THEN
        self.assertEqual(expect, program, f"List element not parsed: {case}")

    @parameterized.expand([
        ("foo(){a = \"test\";}",
         Program({"foo": Function([], [
             BasicAssignment(Identifier("a"), String("test"))])})),
        ("foo(){a = 'test';}",
         Program({"foo": Function([], [
             BasicAssignment(Identifier("a"), String("test"))])})),
        ("foo(){a = 25;}",
         Program({"foo": Function([], [
             BasicAssignment(Identifier("a"), Integer(25))])})),
        ("foo(){a = true;}",
         Program({"foo": Function([], [
             BasicAssignment(Identifier("a"), BoolTrue())])})),
        ("foo(){a = false;}",
         Program({"foo": Function([], [
             BasicAssignment(Identifier("a"), BoolFalse())])})),
        ("foo(){a = null;}",
         Program({"foo": Function([], [
             BasicAssignment(Identifier("a"), Null())])})),
    ])
    def test_try_parse_atom(self, case, expect):
        # GIVEN
        error_handler = ErrorHandler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(lexer, error_handler)

        # WHEN
        program = parser.parse()

        # THEN
        self.assertEqual(expect, program, f"List element not parsed: {case}")
