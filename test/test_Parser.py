import logging
import unittest
from io import StringIO

from parameterized import parameterized

from ErrorHandlerModule.ErrorHandler import ErrorHandler
from ErrorHandlerModule.ErrorType import MissingLeftBracketException, MissingRightBracketException, \
    MissingRightCurlyBracketException, MissingRightSquereBracketException, MissingFunctionBlockException, \
    FunctionRedefinitionException, MissingIdentifierAfterCommaException, MissingExpressionAfterCommaException, \
    MissingSemicolonException, MissingRightSideOfAssignmentException, MissingConditionException, MissingBodyException, \
    MissingIteratorException, MissingIterableException, MissingKeywordInException, ExprMissingRightSideException, \
    MissingIdentifierAfterDotException
from LexerModule.Lexer import Lexer
from ParserModule.Parser import Parser
from ParserModule.Classes import (
    Program, Function, Identifier, BasicAssignment, Integer, AddAssignment, SubAssignment,
    MulAssignment, DivAssignment, ModAssignment, ReturnStatement, AddExpr, SubExpr, IfStatement, GreaterExpr, ElifBlock,
    AndExpr, OrExpr, ElseBlock, FunCall, ForStatement, WhileStatement, MulExpr, EqExpr, NotEqExpr,
    LessExpr, GreaterEqExpr, LessEqExpr, InExpr, DivExpr, ModExpr, IntDivExpr, DotOperator, ListElement, List, String,
    Boolean, Null, Negate, TwoSidedExpression, Assignment, Atom
)


class TestParser(unittest.TestCase):
    @parameterized.expand([
        ("foo(){}", Program({"foo": Function(Identifier("foo"), [], [])})),
        ("foo(){} boo(){}",
         Program({"foo": Function(Identifier("foo"), [], []), "boo": Function(Identifier("boo"), [], [])})),
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
         Program(
             {"foo": Function(Identifier("foo"), [Identifier("a"), Identifier("b")], []),
              "boo": Function(Identifier("boo"), [Identifier("a")], [])
              })),
        ("foo(a, b, c){} boo(){} bar(var){}",
         Program({"foo": Function(Identifier("foo"), [Identifier("a"), Identifier("b"), Identifier("c")], []),
                  "boo": Function(Identifier("boo"), [], []),
                  "bar": Function(Identifier("bar"), [Identifier("var")], [])})),
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
         Program({"foo": Function(Identifier("foo"), [], [BasicAssignment(Identifier("var"), Integer(5))])})),
        ("foo(){var = var1;} boo(){var = var1; var2 = var3;}",
         Program({"foo": Function(Identifier("foo"), [], [BasicAssignment(Identifier("var"), Identifier("var1"))]),
                  "boo": Function(Identifier("boo"), [], [
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
         Program({"foo": Function(Identifier("foo"), [], [BasicAssignment(Identifier("var"), Integer(5))])})),
        ("foo(){var += 5;}",
         Program({"foo": Function(Identifier("foo"), [], [AddAssignment(Identifier("var"), Integer(5))])})),
        ("foo(){var -= 5;}",
         Program({"foo": Function(Identifier("foo"), [], [SubAssignment(Identifier("var"), Integer(5))])})),
        ("foo(){var *= 5;}",
         Program({"foo": Function(Identifier("foo"), [], [MulAssignment(Identifier("var"), Integer(5))])})),
        ("foo(){var /= 5;}",
         Program({"foo": Function(Identifier("foo"), [], [DivAssignment(Identifier("var"), Integer(5))])})),
        ("foo(){var %= 5;}",
         Program({"foo": Function(Identifier("foo"), [], [ModAssignment(Identifier("var"), Integer(5))])})),
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
        ("foo(){return;}",
         Program({"foo": Function(Identifier("foo"), [], [ReturnStatement([])])})),
        ("foo(){return a;}",
         Program({"foo": Function(Identifier("foo"), [], [ReturnStatement([Identifier("a")])])})),
        ("foo(){return a, b;}",
         Program({"foo": Function(Identifier("foo"), [], [ReturnStatement([Identifier("a"), Identifier("b")])])})),
        ("foo(){return a, b + c - 2;}",
         Program({"foo": Function(Identifier("foo"), [], [
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
        ("foo(){if(true) a += 1;}",
         Program({"foo": Function(Identifier("foo"), [], [
             IfStatement(Boolean(True), [AddAssignment(Identifier("a"), Integer(1))],
                         [], None)])})),
        ("foo(){if(a > b){a += 1;}}",
         Program({"foo": Function(Identifier("foo"), [], [
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
         Program({"foo": Function(Identifier("foo"), [], [
             IfStatement(GreaterExpr(Identifier("a"), Identifier("b")), [AddAssignment(Identifier("a"), Integer(1))],
                         [ElifBlock(AndExpr(Identifier("c"), Identifier("d")),
                                    [AddAssignment(Identifier("e"), Integer(1))])], None)])})),
        ("foo(){if(a > b){a += 1;} elif(c and d){e += 1;} elif(d or f){e = 1;}}",
         Program({"foo": Function(Identifier("foo"), [], [
             IfStatement(GreaterExpr(Identifier("a"), Identifier("b")), [AddAssignment(Identifier("a"), Integer(1))],
                         [ElifBlock(AndExpr(Identifier("c"), Identifier("d")),
                                    [AddAssignment(Identifier("e"), Integer(1))]),
                          ElifBlock(OrExpr(Identifier("d"), Identifier("f")),
                                    [BasicAssignment(Identifier("e"), Integer(1))])], None)])})),
        ("foo(){if(a > b){a += 1;} elif(c and d){e += 1;} elif(d or f){e = 1;} else{print(a);}}",
         Program({"foo": Function(Identifier("foo"), [], [
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
         Program({"foo": Function(Identifier("foo"), [], [
             IfStatement(GreaterExpr(Identifier("a"), Identifier("b")), [AddAssignment(Identifier("a"), Integer(1))],
                         [],
                         ElseBlock([FunCall(Identifier("print"), [Identifier("a")])]))])})),
        ("foo(){if(a > b){a += 1;} elif(c and d){e += 1;} elif(d or f){e = 1;} else{print(a);}}",
         Program({"foo": Function(Identifier("foo"), [], [
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
        ("foo(){for(a in b)print(a);}",
         Program({"foo": Function(Identifier("foo"), [], [
             ForStatement(Identifier("a"), Identifier("b"), [FunCall(Identifier("print"), [Identifier("a")])])])})),
        ("foo(){for(a in b){print(a);}}",
         Program({"foo": Function(Identifier("foo"), [], [
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
        ("foo(){while(a and b)print(a);}",
         Program({"foo": Function(Identifier("foo"), [], [
             WhileStatement(AndExpr(Identifier("a"), Identifier("b")),
                            [FunCall(Identifier("print"), [Identifier("a")])])])})),
        ("foo(){while(true){print(a);}}",
         Program({"foo": Function(Identifier("foo"), [], [
             WhileStatement(Boolean(True),
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
        ("foo(){a = -a and b or c - 2 * 3 and (b or not g);}",
         Program({"foo": Function(Identifier("foo"), [], [
             BasicAssignment(
                 Identifier("a"),
                 OrExpr(AndExpr(Negate(Identifier("a")), Identifier("b")),
                        AndExpr(
                            SubExpr(Identifier("c"),
                                    MulExpr(Integer(2), Integer(3))),
                            OrExpr(Identifier("b"), Negate(Identifier("g"))))))])})),
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
         Program({"foo": Function(Identifier("foo"), [],
                                  [BasicAssignment(Identifier("a"), OrExpr(Identifier("c"), Identifier("b")))])})),
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
         Program({"foo": Function(Identifier("foo"), [],
                                  [BasicAssignment(Identifier("a"), AndExpr(Identifier("c"), Identifier("b")))])})),
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
         Program({"foo": Function(Identifier("foo"), [],
                                  [BasicAssignment(Identifier("a"), Negate(Identifier("b")))])})),
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
        ("foo(){a = b == c;}", Program({"foo": Function(Identifier("foo"), [], [
            BasicAssignment(Identifier("a"), EqExpr(Identifier("b"), Identifier("c")))])})),
        ("foo(){a = b != c;}", Program({"foo": Function(Identifier("foo"), [], [
            BasicAssignment(Identifier("a"), NotEqExpr(Identifier("b"), Identifier("c")))])})),
        ("foo(){a = b > c;}", Program({"foo": Function(Identifier("foo"), [], [
            BasicAssignment(Identifier("a"), GreaterExpr(Identifier("b"), Identifier("c")))])})),
        ("foo(){a = b < c;}", Program({"foo": Function(Identifier("foo"), [], [
            BasicAssignment(Identifier("a"), LessExpr(Identifier("b"), Identifier("c")))])})),
        ("foo(){a = b >= c;}", Program({"foo": Function(Identifier("foo"), [], [
            BasicAssignment(Identifier("a"), GreaterEqExpr(Identifier("b"), Identifier("c")))])})),
        ("foo(){a = b <= c;}", Program({"foo": Function(Identifier("foo"), [], [
            BasicAssignment(Identifier("a"), LessEqExpr(Identifier("b"), Identifier("c")))])})),
        ("foo(){a = b in c;}", Program({"foo": Function(Identifier("foo"), [], [
            BasicAssignment(Identifier("a"), InExpr(Identifier("b"), Identifier("c")))])})),
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
        ("foo(){a = b + c;}", Program({"foo": Function(Identifier("foo"), [], [
            BasicAssignment(Identifier("a"), AddExpr(Identifier("b"), Identifier("c")))])})),
        ("foo(){a = b - c;}", Program({"foo": Function(Identifier("foo"), [], [
            BasicAssignment(Identifier("a"), SubExpr(Identifier("b"), Identifier("c")))])})),
        ("foo(){a = b + c - d;}", Program({"foo": Function(Identifier("foo"), [], [
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
        ("foo(){a = b * c;}", Program({"foo": Function(Identifier("foo"), [], [
            BasicAssignment(Identifier("a"), MulExpr(Identifier("b"), Identifier("c")))])})),
        ("foo(){a = b / c;}", Program({"foo": Function(Identifier("foo"), [], [
            BasicAssignment(Identifier("a"), DivExpr(Identifier("b"), Identifier("c")))])})),
        ("foo(){a = b % c;}", Program({"foo": Function(Identifier("foo"), [], [
            BasicAssignment(Identifier("a"), ModExpr(Identifier("b"), Identifier("c")))])})),
        ("foo(){a = b // c;}", Program({"foo": Function(Identifier("foo"), [], [
            BasicAssignment(Identifier("a"), IntDivExpr(Identifier("b"), Identifier("c")))])})),
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
        ("foo(){a = b.c;}", Program({"foo": Function(Identifier("foo"), [], [
            BasicAssignment(Identifier("a"), DotOperator(Identifier("b"), Identifier("c")))])})),
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
        ("foo(){a = b();}", Program({"foo": Function(Identifier("foo"), [], [
            BasicAssignment(Identifier("a"), FunCall(Identifier("b"), []))])})),
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
        ("foo(){a = b(a, b, 5);}", Program({"foo": Function(Identifier("foo"), [], [
            BasicAssignment(Identifier("a"), FunCall(Identifier("b"), [Identifier("a"), Identifier("b"), Integer(5)]))
        ])})),
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
        ("foo(){a = b[1];}", Program({"foo": Function(Identifier("foo"), [], [
            BasicAssignment(Identifier("a"), ListElement(Identifier("b"), Integer(1)))])})),
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
         Program({"foo": Function(Identifier("foo"), [], [
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
        self.assertEqual(expect, program, f"Parenthesis not parsed: {case}")

    @parameterized.expand([
        ("foo(){a = [1, 2, 3];}",
         Program({"foo": Function(Identifier("foo"), [], [
             BasicAssignment(Identifier("a"), List([Integer(1), Integer(2), Integer(3)]))])})),
        ("foo(){a = [];}",
         Program({"foo": Function(Identifier("foo"), [], [
             BasicAssignment(Identifier("a"), List([]))])})),
    ])
    def test_try_parse_list(self, case, expect):
        # GIVEN
        error_handler = ErrorHandler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(lexer, error_handler)

        # WHEN
        program = parser.parse()

        # THEN
        self.assertEqual(expect, program, f"List not parsed: {case}")

    @parameterized.expand([
        ("foo(){a = \"test\";}",
         Program({"foo": Function(Identifier("foo"), [], [
             BasicAssignment(Identifier("a"), String("test"))])})),
        ("foo(){a = 'test';}",
         Program({"foo": Function(Identifier("foo"), [], [
             BasicAssignment(Identifier("a"), String("test"))])})),
        ("foo(){a = 25;}",
         Program({"foo": Function(Identifier("foo"), [], [
             BasicAssignment(Identifier("a"), Integer(25))])})),
        ("foo(){a = true;}",
         Program({"foo": Function(Identifier("foo"), [], [
             BasicAssignment(Identifier("a"), Boolean(True))])})),
        ("foo(){a = false;}",
         Program({"foo": Function(Identifier("foo"), [], [
             BasicAssignment(Identifier("a"), Boolean(False))])})),
        ("foo(){a = null;}",
         Program({"foo": Function(Identifier("foo"), [], [
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
        self.assertEqual(expect, program, f"Atom not parsed: {case}")


class TestParserErrorHandling(unittest.TestCase):
    @parameterized.expand([
        ("foo)",
         MissingLeftBracketException),
        ("foo(){if)}",
         MissingLeftBracketException),
        ("foo(){if(true){}elif)}",
         MissingLeftBracketException),
        ("foo(){for)}",
         MissingLeftBracketException),
        ("foo(){while)}",
         MissingLeftBracketException),
        ("foo({}",
         MissingRightBracketException),
        ("foo(){if(true{}}",
         MissingRightBracketException),
        ("foo(){if(true){}elif(true{}}",
         MissingRightBracketException),
        ("foo(){for(a in b{}}",
         MissingRightBracketException),
        ("foo(){while(true{}}",
         MissingRightBracketException),
        ("foo(){boo(}",
         MissingRightBracketException),
        ("foo(){(a + b}",
         MissingRightBracketException),
        ("foo(){",
         MissingRightCurlyBracketException),
        ("foo(){[}",
         MissingRightSquereBracketException),
        ("foo(){[a}",
         MissingRightSquereBracketException),
        ("foo(){a[}",
         MissingRightSquereBracketException),
        ("foo(){a[1}",
         MissingRightSquereBracketException),
    ])
    def test_detect_missing_brackets(self, case, expect):
        # GIVEN
        # error_handler = ErrorHandler(logging.CRITICAL)
        error_handler = ErrorHandler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(lexer, error_handler)

        # THEN
        self.assertRaises(expect, parser.parse)

    @parameterized.expand([
        ("foo()",
         MissingFunctionBlockException),
        ("foo(){}boo()",
         MissingFunctionBlockException),
    ])
    def test_detect_missing_function_body(self, case, expect):
        # GIVEN
        # error_handler = ErrorHandler(logging.CRITICAL)
        error_handler = ErrorHandler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(lexer, error_handler)

        # THEN
        self.assertRaises(expect, parser.parse)

    @parameterized.expand([
        ("foo(){}foo(){}",
         FunctionRedefinitionException),
        ("foo(){}boo(){}foo(){}",
         FunctionRedefinitionException),
    ])
    def test_detect_function_redefinition(self, case, expect):
        # GIVEN
        # error_handler = ErrorHandler(logging.CRITICAL)
        error_handler = ErrorHandler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(lexer, error_handler)

        # THEN
        self.assertRaises(expect, parser.parse)

    @parameterized.expand([
        ("foo(a,)",
         MissingIdentifierAfterCommaException),
        ("foo(a,c){}boo(a,b,){}",
         MissingIdentifierAfterCommaException),
        ("foo(a,){}boo(a,b){}",
         MissingIdentifierAfterCommaException),
    ])
    def test_detect_missing_identifier_after_comma(self, case, expect):
        # GIVEN
        # error_handler = ErrorHandler(logging.CRITICAL)
        error_handler = ErrorHandler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(lexer, error_handler)

        # THEN
        self.assertRaises(expect, parser.parse)

    @parameterized.expand([
        ("foo(){return a,;}",
         MissingExpressionAfterCommaException),
        ("foo(){boo(a,)}",
         MissingExpressionAfterCommaException),
        ("foo(){[1,]}",
         MissingExpressionAfterCommaException),
    ])
    def test_detect_missing_expression_after_comma(self, case, expect):
        # GIVEN
        # error_handler = ErrorHandler(logging.CRITICAL)
        error_handler = ErrorHandler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(lexer, error_handler)

        # THEN
        self.assertRaises(expect, parser.parse)

    @parameterized.expand([
        ("foo(){print()}",
         MissingSemicolonException),
        ("foo(){a = 1}",
         MissingSemicolonException),
        ("foo(){a = 1; b = a + 5}",
         MissingSemicolonException),
    ])
    def test_detect_missing_expression_after_comma(self, case, expect):
        # GIVEN
        # error_handler = ErrorHandler(logging.CRITICAL)
        error_handler = ErrorHandler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(lexer, error_handler)

        # THEN
        self.assertRaises(expect, parser.parse)

    @parameterized.expand([
        ("foo(){a = }",
         MissingRightSideOfAssignmentException),
    ])
    def test_detect_missing_expression_after_comma(self, case, expect):
        # GIVEN
        # error_handler = ErrorHandler(logging.CRITICAL)
        error_handler = ErrorHandler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(lexer, error_handler)

        # THEN
        self.assertRaises(expect, parser.parse)

    @parameterized.expand([
        ("foo(){if(){}}",
         MissingConditionException),
        ("foo(){if(true){}elif(){}}",
         MissingConditionException),
        ("foo(){while(){}}",
         MissingConditionException),
    ])
    def test_detect_missing_condition(self, case, expect):
        # GIVEN
        # error_handler = ErrorHandler(logging.CRITICAL)
        error_handler = ErrorHandler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(lexer, error_handler)

        # THEN
        self.assertRaises(expect, parser.parse)

    @parameterized.expand([
        ("foo(){if(true)}",
         MissingBodyException),
        ("foo(){if(true){}elif(true)}",
         MissingBodyException),
        ("foo(){if(true){}else}",
         MissingBodyException),
        ("foo(){for(a in b)}",
         MissingBodyException),
        ("foo(){while(true)}",
         MissingBodyException),
    ])
    def test_detect_missing_body(self, case, expect):
        # GIVEN
        # error_handler = ErrorHandler(logging.CRITICAL)
        error_handler = ErrorHandler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(lexer, error_handler)

        # THEN
        self.assertRaises(expect, parser.parse)

    @parameterized.expand([
        ("foo(){for()}",
         MissingIteratorException),
    ])
    def test_detect_missing_iterator(self, case, expect):
        # GIVEN
        # error_handler = ErrorHandler(logging.CRITICAL)
        error_handler = ErrorHandler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(lexer, error_handler)

        # THEN
        self.assertRaises(expect, parser.parse)

    @parameterized.expand([
        ("foo(){for(a)}",
         MissingKeywordInException),
    ])
    def test_detect_missing_in_keyword(self, case, expect):
        # GIVEN
        # error_handler = ErrorHandler(logging.CRITICAL)
        error_handler = ErrorHandler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(lexer, error_handler)

        # THEN
        self.assertRaises(expect, parser.parse)

    @parameterized.expand([
        ("foo(){for(a in)}",
         MissingIterableException),
    ])
    def test_detect_missing_iterable(self, case, expect):
        # GIVEN
        # error_handler = ErrorHandler(logging.CRITICAL)
        error_handler = ErrorHandler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(lexer, error_handler)

        # THEN
        self.assertRaises(expect, parser.parse)

    @parameterized.expand([
        ("foo(){a or}",
         ExprMissingRightSideException),
        ("foo(){a and}",
         ExprMissingRightSideException),
        ("foo(){not}",
         ExprMissingRightSideException),
        ("foo(){not}",
         ExprMissingRightSideException),
        ("foo(){a ==}",
         ExprMissingRightSideException),
        ("foo(){a !=}",
         ExprMissingRightSideException),
        ("foo(){a <}",
         ExprMissingRightSideException),
        ("foo(){a >}",
         ExprMissingRightSideException),
        ("foo(){a <=}",
         ExprMissingRightSideException),
        ("foo(){a >=}",
         ExprMissingRightSideException),
        ("foo(){a in}",
         ExprMissingRightSideException),
        ("foo(){a +}",
         ExprMissingRightSideException),
        ("foo(){a -}",
         ExprMissingRightSideException),
        ("foo(){a *}",
         ExprMissingRightSideException),
        ("foo(){a /}",
         ExprMissingRightSideException),
        ("foo(){a %}",
         ExprMissingRightSideException),
        ("foo(){a //}",
         ExprMissingRightSideException),
        ("foo(){-}",
         ExprMissingRightSideException),
        ("foo(){-+---}",
         ExprMissingRightSideException),
    ])
    def test_detect_missing_right_side_expression(self, case, expect):
        # GIVEN
        # error_handler = ErrorHandler(logging.CRITICAL)
        error_handler = ErrorHandler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(lexer, error_handler)

        # THEN
        self.assertRaises(expect, parser.parse)

    @parameterized.expand([
        ("foo(){a.}",
         MissingIdentifierAfterDotException),
    ])
    def test_detect_missing_identifier_after_dot(self, case, expect):
        # GIVEN
        # error_handler = ErrorHandler(logging.CRITICAL)
        error_handler = ErrorHandler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(lexer, error_handler)

        # THEN
        self.assertRaises(expect, parser.parse)


class TestParserClasses(unittest.TestCase):
    @parameterized.expand([
        (Identifier("a"),),
        (Null(),),
        (String("test"),),
        (Atom(String("a")),),
        (FunCall(Identifier("print"), List([Integer(2)])),),
        (TwoSidedExpression(Identifier("a"), Integer(2)),),
        (WhileStatement(Boolean(True), [FunCall(Identifier("print"), List([Integer(2)]))]),),
        (ForStatement(Identifier("a"), Identifier("a"), [FunCall(Identifier("print"), List([Integer(2)]))]),),
        (IfStatement(Boolean(True), [FunCall(Identifier("print"), List([Integer(2)]))],
                     [ElifBlock(Boolean(True), [FunCall(Identifier("print"), List([Integer(2)]))])],
                     ElseBlock([FunCall(Identifier("print"), List([Integer(2)]))])),),
        (ReturnStatement([Identifier("a")]),),
        (Assignment(Identifier("a"), Integer(2)),),
        (Function(Identifier("a"), [Identifier("b")], [Assignment(Identifier("a"), Integer(2))]),),
        (Program({"a": Function(Identifier("a"), [Identifier("b")], [Assignment(Identifier("a"), Integer(2))])}),),
    ])
    def test_check_classes_repr(self, case):
        # GIVEN
        str_repr = f"{case}"
        loc = {}

        # WHEN
        exec(f"new_object = {str_repr}", globals(), loc)

        # THEN
        self.assertEqual(case, loc["new_object"], f"Class {case.__class__} has wrong __repr__.")

    @parameterized.expand([
        (Atom(String("a")),),
        (TwoSidedExpression(Identifier("a"), Integer(2)),),
        (WhileStatement(Boolean(True), [FunCall(Identifier("print"), List([Integer(2)]))]),),
        (ForStatement(Identifier("a"), Identifier("a"), [FunCall(Identifier("print"), List([Integer(2)]))]),),
        (IfStatement(Boolean(True), [FunCall(Identifier("print"), List([Integer(2)]))], []),),
        (ElifBlock(Boolean(True), [FunCall(Identifier("print"), List([Integer(2)]))]),),
        (ElseBlock([FunCall(Identifier("print"), List([Integer(2)]))]),),
        (ReturnStatement([Identifier("a")]),),
        (Assignment(Identifier("a"), Integer(2)),),
        (Function(Identifier("a"), [Identifier("b")], [Assignment(Identifier("a"), Integer(2))]),),
        (Program({"a": Function(Identifier("a"), [Identifier("b")], [Assignment(Identifier("a"), Integer(2))])}),),
    ])
    def test_check_objects_equality(self, case):
        self.assertEqual(case, case, f"Class {case.__class__} has wrong __eq__.")

    @parameterized.expand([
        (Atom(String("a")),
         Atom(String("b"))),
        (TwoSidedExpression(Identifier("a"), Integer(2)),
         TwoSidedExpression(Identifier("b"), Integer(2))),
        (TwoSidedExpression(Identifier("a"), Integer(2)),
         TwoSidedExpression(Identifier("a"), Integer(1))),
        (WhileStatement(Boolean(True), [FunCall(Identifier("print"), List([Integer(2)]))]),
         WhileStatement(Boolean(False), [FunCall(Identifier("print"), List([Integer(2)]))])),
        (WhileStatement(Boolean(True), [FunCall(Identifier("print"), List([Integer(2)]))]),
         WhileStatement(Boolean(True), [TwoSidedExpression(Identifier("a"), Integer(2))])),
        (ForStatement(Identifier("a"), Identifier("a"), [FunCall(Identifier("print"), List([Integer(2)]))]),
         ForStatement(Identifier("b"), Identifier("a"), [FunCall(Identifier("print"), List([Integer(2)]))])),
        (ForStatement(Identifier("a"), Identifier("a"), [FunCall(Identifier("print"), List([Integer(2)]))]),
         ForStatement(Identifier("a"), Identifier("b"), [FunCall(Identifier("print"), List([Integer(2)]))])),
        (ForStatement(Identifier("a"), Identifier("a"), [FunCall(Identifier("print"), List([Integer(2)]))]),
         ForStatement(Identifier("a"), Identifier("a"), [TwoSidedExpression(Identifier("a"), Integer(2))])),
        (IfStatement(Boolean(True), [FunCall(Identifier("print"), List([Integer(2)]))], []),
         IfStatement(Boolean(False), [FunCall(Identifier("print"), List([Integer(2)]))], [])),
        (IfStatement(Boolean(True), [FunCall(Identifier("print"), List([Integer(2)]))], []),
         IfStatement(Boolean(True), [TwoSidedExpression(Identifier("a"), Integer(2))], [])),
        (IfStatement(Boolean(True), [FunCall(Identifier("print"), List([Integer(2)]))], []),
         IfStatement(Boolean(True), [FunCall(Identifier("print"), List([Integer(2)]))],
                     [ElifBlock(Boolean(True), [FunCall(Identifier("print"), List([Integer(2)]))])])),
        (IfStatement(Boolean(True), [FunCall(Identifier("print"), List([Integer(2)]))],
                     [ElifBlock(Boolean(False), [FunCall(Identifier("print"), List([Integer(2)]))])]),
         IfStatement(Boolean(True), [FunCall(Identifier("print"), List([Integer(2)]))],
                     [ElifBlock(Boolean(True), [FunCall(Identifier("print"), List([Integer(2)]))])])),
        (IfStatement(Boolean(True), [FunCall(Identifier("print"), List([Integer(2)]))], []),
         IfStatement(Boolean(True), [FunCall(Identifier("print"), List([Integer(2)]))], [],
                     ElseBlock([FunCall(Identifier("print"), List([Integer(2)]))]))),
        (IfStatement(Boolean(True), [FunCall(Identifier("print"), List([Integer(2)]))], [],
                     ElseBlock([FunCall(Identifier("input"), List([String("test")]))])),
         IfStatement(Boolean(True), [FunCall(Identifier("print"), List([Integer(2)]))], [],
                     ElseBlock([FunCall(Identifier("print"), List([Integer(2)]))]))),
        (ElifBlock(Boolean(True), [FunCall(Identifier("print"), List([Integer(2)]))]),
         ElifBlock(Boolean(False), [FunCall(Identifier("print"), List([Integer(2)]))])),
        (ElifBlock(Boolean(True), [FunCall(Identifier("print"), List([Integer(2)]))]),
         ElifBlock(Boolean(True), [TwoSidedExpression(Identifier("a"), Integer(2))])),
        (ElseBlock([FunCall(Identifier("print"), List([Integer(2)]))]),
         ElseBlock([TwoSidedExpression(Identifier("a"), Integer(2))])),
        (ReturnStatement([Identifier("a")]),
         ReturnStatement([Identifier("b")])),
        (Assignment(Identifier("a"), Integer(2)),
         Assignment(Identifier("b"), Integer(2))),
        (Assignment(Identifier("a"), Integer(2)),
         Assignment(Identifier("a"), Integer(1))),
        (Function(Identifier("a"), [Identifier("b")], [Assignment(Identifier("a"), Integer(2))]),
         Function(Identifier("b"), [Identifier("b")], [Assignment(Identifier("a"), Integer(2))])),
        (Function(Identifier("a"), [Identifier("b")], [Assignment(Identifier("a"), Integer(2))]),
         Function(Identifier("a"), [Identifier("c")], [Assignment(Identifier("a"), Integer(2))])),
        (Function(Identifier("a"), [Identifier("b")], [Assignment(Identifier("a"), Integer(2))]),
         Function(Identifier("a"), [Identifier("b")], [FunCall(Identifier("print"), List([Integer(2)]))])),
        (Program({"a": Function(Identifier("a"), [Identifier("b")], [Assignment(Identifier("a"), Integer(2))])}),
         Program({"b": Function(Identifier("b"), [Identifier("b")], [Assignment(Identifier("a"), Integer(2))])})),
    ])
    def test_check_objects_inequality(self, case, compare):
        self.assertNotEqual(compare, case, f"Class {case.__class__} has wrong __eq__.")
