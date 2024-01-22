import logging
import unittest
from io import StringIO

from parameterized import parameterized

from Tutel.common.ErrorHandler import ErrorHandler
from Tutel.common.ErrorType import MissingLeftBracketException, MissingRightBracketException, \
    MissingRightCurlyBracketException, MissingRightSquareBracketException, MissingFunctionBlockException, \
    FunctionRedefinitionException, MissingIdentifierAfterCommaException, MissingExpressionAfterCommaException, \
    MissingSemicolonException, MissingRightSideOfAssignmentException, MissingConditionException, MissingBodyException, \
    MissingIteratorException, MissingIterableException, MissingKeywordInException, ExprMissingRightSideException, \
    MissingIdentifierAfterDotException
from Tutel.core.LexerModule.Lexer import Lexer
from Tutel.core.ParserModule.Classes import (
    Program, Function, Identifier, BasicAssignment, Integer, AddAssignment, SubAssignment,
    MulAssignment, DivAssignment, ModAssignment, ReturnStatement, AddExpr, SubExpr, IfStatement, GreaterExpr, ElifBlock,
    AndExpr, OrExpr, ElseBlock, FunCall, ForStatement, WhileStatement, MulExpr, EqExpr, NotEqExpr,
    LessExpr, GreaterEqExpr, LessEqExpr, InExpr, DivExpr, ModExpr, IntDivExpr, DotOperator, ListElement, List, String,
    Boolean, Null, Negate, TwoSidedExpression, Assignment, Atom, Block, InvertExpr
)
from Tutel.core.ParserModule.Parser import Parser


class TestParser(unittest.TestCase):
    @parameterized.expand([
        ("#test\nfoo(){}", Program({"foo": Function(Identifier("foo", 2), [], Block([], 2), 2)}, lineno=1)),
        ("foo(){a = 1; #test\n}",
         Program(
             {"foo": Function(Identifier("foo", lineno=1), [],
                              Block([BasicAssignment(Identifier("a", lineno=1), Integer(1, lineno=1), lineno=1)],
                                    lineno=1), lineno=1)}, lineno=1)),
    ])
    def test_skip_comment(self, case, expect):
        # GIVEN
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(error_handler)

        # WHEN
        program = parser.parse(lexer)

        # THEN
        self.assertEqual(expect, program, f"Function not parsed: {case}")

    @parameterized.expand([
        ("foo(){}",
         Program({"foo": Function(Identifier("foo", lineno=1), [], Block([], lineno=1), lineno=1)}, lineno=1)),
        ("foo(){} boo(){}",
         Program(
             {"foo": Function(Identifier("foo", lineno=1), [], Block([], lineno=1), lineno=1),
              "boo": Function(Identifier("boo", lineno=1), [], Block([], lineno=1), lineno=1)}, lineno=1)),
    ])
    def test_try_parse_function_def(self, case, expect):
        # GIVEN
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(error_handler)

        # WHEN
        program = parser.parse(lexer)

        # THEN
        self.assertEqual(expect, program, f"Function not parsed: {case}")

    @parameterized.expand([
        ("foo(a, b){} boo(a){}",
         Program(
             {"foo": Function(Identifier("foo", lineno=1), [Identifier("a", lineno=1), Identifier("b", lineno=1)],
                              Block([], lineno=1), lineno=1),
              "boo": Function(Identifier("boo", lineno=1), [Identifier("a", lineno=1)], Block([], lineno=1), lineno=1)
              }, lineno=1)),
        ("foo(a, b, c){} boo(){} bar(var){}",
         Program({"foo": Function(Identifier("foo", lineno=1),
                                  [Identifier("a", lineno=1), Identifier("b", lineno=1), Identifier("c", lineno=1)],
                                  Block([], lineno=1), lineno=1),
                  "boo": Function(Identifier("boo", lineno=1), [], Block([], lineno=1), lineno=1),
                  "bar": Function(Identifier("bar", lineno=1), [Identifier("var", lineno=1)], Block([], lineno=1),
                                  lineno=1)}, lineno=1)),
    ])
    def test_try_parse_params_list(self, case, expect):
        # GIVEN
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(error_handler)

        # WHEN
        program = parser.parse(lexer)

        # THEN
        self.assertEqual(expect, program, f"Function params not parsed: {case}")

    @parameterized.expand([
        ("foo(){var = 5;}",
         Program({"foo": Function(Identifier("foo", lineno=1), [],
                                  Block([BasicAssignment(Identifier("var", lineno=1), Integer(5, lineno=1), lineno=1)],
                                        lineno=1), lineno=1)}, lineno=1)),
        ("foo(){var = var1;} boo(){var = var1; var2 = var3;}",
         Program(
             {"foo": Function(Identifier("foo", lineno=1), [],
                              Block([BasicAssignment(Identifier("var", lineno=1), Identifier("var1", lineno=1),
                                                     lineno=1)], lineno=1), lineno=1),
              "boo": Function(Identifier("boo", lineno=1), [], Block([
                  BasicAssignment(Identifier("var", lineno=1), Identifier("var1", lineno=1), lineno=1),
                  BasicAssignment(Identifier("var2", lineno=1), Identifier("var3", lineno=1), lineno=1)], lineno=1),
                              lineno=1)}, lineno=1)),
    ])
    def test_try_parse_block(self, case, expect):
        # GIVEN
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(error_handler)

        # WHEN
        program = parser.parse(lexer)

        # THEN
        self.assertEqual(expect, program, f"Function block not parsed: {case}")

    @parameterized.expand([
        ("foo(){var = 5;}",
         Program({"foo": Function(Identifier("foo", lineno=1), [],
                                  Block([BasicAssignment(Identifier("var", lineno=1), Integer(5, lineno=1), lineno=1)],
                                        lineno=1), lineno=1)}, lineno=1)),
        ("foo(){var += 5;}",
         Program({"foo": Function(Identifier("foo", lineno=1), [],
                                  Block([AddAssignment(Identifier("var", lineno=1), Integer(5, lineno=1), lineno=1)],
                                        lineno=1), lineno=1)}, lineno=1)),
        ("foo(){var -= 5;}",
         Program({"foo": Function(Identifier("foo", lineno=1), [],
                                  Block([SubAssignment(Identifier("var", lineno=1), Integer(5, lineno=1), lineno=1)],
                                        lineno=1), lineno=1)}, lineno=1)),
        ("foo(){var *= 5;}",
         Program({"foo": Function(Identifier("foo", lineno=1), [],
                                  Block([MulAssignment(Identifier("var", lineno=1), Integer(5, lineno=1), lineno=1)],
                                        lineno=1), lineno=1)}, lineno=1)),
        ("foo(){var /= 5;}",
         Program({"foo": Function(Identifier("foo", lineno=1), [],
                                  Block([DivAssignment(Identifier("var", lineno=1), Integer(5, lineno=1), lineno=1)],
                                        lineno=1), lineno=1)}, lineno=1)),
        ("foo(){var %= 5;}",
         Program({"foo": Function(Identifier("foo", lineno=1), [],
                                  Block([ModAssignment(Identifier("var", lineno=1), Integer(5, lineno=1), lineno=1)],
                                        lineno=1), lineno=1)}, lineno=1)),
    ])
    def test_try_parse_assignment(self, case, expect):
        # GIVEN
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(error_handler)

        # WHEN
        program = parser.parse(lexer)

        # THEN
        self.assertEqual(expect, program, f"Assignment not parsed: {case}")

    @parameterized.expand([
        ("foo(){return;}",
         Program({"foo": Function(Identifier("foo", lineno=1), [], Block([ReturnStatement([], lineno=1)], lineno=1),
                                  lineno=1)}, lineno=1)),
        ("foo(){return a;}",
         Program({"foo": Function(Identifier("foo", lineno=1), [],
                                  Block([ReturnStatement([Identifier("a", lineno=1)], lineno=1)], lineno=1), lineno=1)},
                 1)),
        ("foo(){return a, b;}",
         Program(
             {"foo": Function(Identifier("foo", lineno=1), [],
                              Block([ReturnStatement([Identifier("a", lineno=1), Identifier("b", lineno=1)], lineno=1)],
                                    lineno=1), lineno=1)}, lineno=1)),
        ("foo(){return a, b + c - 2;}",
         Program({"foo": Function(Identifier("foo", lineno=1), [], Block([
             ReturnStatement(
                 [Identifier("a", lineno=1),
                  SubExpr(AddExpr(Identifier("b", lineno=1), Identifier("c", lineno=1), lineno=1), Integer(2, lineno=1),
                          lineno=1)],
                 1)], lineno=1), lineno=1)}, lineno=1)),
    ])
    def test_try_parse_return_statement(self, case, expect):
        # GIVEN
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(error_handler)

        # WHEN
        program = parser.parse(lexer)

        # THEN
        self.assertEqual(expect, program, f"Return statement not parsed: {case}")

    @parameterized.expand([
        ("foo(){if(true) a += 1;}",
         Program({"foo": Function(Identifier("foo", lineno=1), [], Block([
             IfStatement(Boolean(True, lineno=1),
                         Block([AddAssignment(Identifier("a", lineno=1), Integer(1, lineno=1), lineno=1)], lineno=1),
                         [], None, lineno=1)], lineno=1), lineno=1)}, lineno=1)),
        ("foo(){if(a > b){a += 1;}}",
         Program({"foo": Function(Identifier("foo", lineno=1), [], Block([
             IfStatement(GreaterExpr(Identifier("a", lineno=1), Identifier("b", lineno=1), lineno=1),
                         Block([AddAssignment(Identifier("a", lineno=1), Integer(1, lineno=1), lineno=1)], lineno=1),
                         [], None, lineno=1)], lineno=1), lineno=1)}, lineno=1)),
    ])
    def test_try_parse_if_statement(self, case, expect):
        # GIVEN
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(error_handler)

        # WHEN
        program = parser.parse(lexer)

        # THEN
        self.assertEqual(expect, program, f"If statement not parsed: {case}")

    @parameterized.expand([
        ("foo(){if(a > b){a += 1;} elif(c and d){e += 1;}}",
         Program({"foo": Function(Identifier("foo", lineno=1), [], Block([
             IfStatement(GreaterExpr(Identifier("a", lineno=1), Identifier("b", lineno=1), lineno=1),
                         Block([AddAssignment(Identifier("a", lineno=1), Integer(1, lineno=1), lineno=1)], lineno=1),
                         [ElifBlock(AndExpr(Identifier("c", lineno=1), Identifier("d", lineno=1), lineno=1),
                                    Block([AddAssignment(Identifier("e", lineno=1), Integer(1, lineno=1), lineno=1)],
                                          lineno=1), lineno=1)], None, lineno=1)], lineno=1),
                                  1)}, lineno=1)),
        ("foo(){if(a > b){a += 1;} elif(c and d){e += 1;} elif(d or f){e = 1;}}",
         Program({"foo": Function(Identifier("foo", lineno=1), [], Block([
             IfStatement(GreaterExpr(Identifier("a", lineno=1), Identifier("b", lineno=1), lineno=1),
                         Block([AddAssignment(Identifier("a", lineno=1), Integer(1, lineno=1), lineno=1)], lineno=1),
                         [ElifBlock(AndExpr(Identifier("c", lineno=1), Identifier("d", lineno=1), lineno=1),
                                    Block([AddAssignment(Identifier("e", lineno=1), Integer(1, lineno=1), lineno=1)],
                                          lineno=1), lineno=1),
                          ElifBlock(OrExpr(Identifier("d", lineno=1), Identifier("f", lineno=1), lineno=1),
                                    Block([BasicAssignment(Identifier("e", lineno=1), Integer(1, lineno=1), lineno=1)],
                                          lineno=1), lineno=1)], None, lineno=1)],
             1), lineno=1)}, lineno=1)),
        ("foo(){if(a > b){a += 1;} elif(c and d){e += 1;} elif(d or f){e = 1;} else{print(a);}}",
         Program({"foo": Function(Identifier("foo", lineno=1), [], Block([
             IfStatement(GreaterExpr(Identifier("a", lineno=1), Identifier("b", lineno=1), lineno=1),
                         Block([AddAssignment(Identifier("a", lineno=1), Integer(1, lineno=1), lineno=1)], lineno=1),
                         [ElifBlock(AndExpr(Identifier("c", lineno=1), Identifier("d", lineno=1), lineno=1),
                                    Block([AddAssignment(Identifier("e", lineno=1), Integer(1, lineno=1), lineno=1)],
                                          lineno=1), lineno=1),
                          ElifBlock(OrExpr(Identifier("d", lineno=1), Identifier("f", lineno=1), lineno=1),
                                    Block([BasicAssignment(Identifier("e", lineno=1), Integer(1, lineno=1), lineno=1)],
                                          lineno=1), lineno=1)],
                         ElseBlock(
                             Block([FunCall(Identifier("print", lineno=1), [Identifier("a", lineno=1)], lineno=1)],
                                   lineno=1), lineno=1), lineno=1)], lineno=1),
                                  1)}, lineno=1)),
    ])
    def test_try_parse_elif_block(self, case, expect):
        # GIVEN
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(error_handler)

        # WHEN
        program = parser.parse(lexer)

        # THEN
        self.assertEqual(expect, program, f"Elif statement not parsed: {case}")

    @parameterized.expand([
        ("foo(){if(a > b){a += 1;} else{print(a);}}",
         Program({"foo": Function(Identifier("foo", lineno=1), [], Block([
             IfStatement(GreaterExpr(Identifier("a", lineno=1), Identifier("b", lineno=1), lineno=1),
                         Block([AddAssignment(Identifier("a", lineno=1), Integer(1, lineno=1), lineno=1)], lineno=1),
                         [],
                         ElseBlock(
                             Block([FunCall(Identifier("print", lineno=1), [Identifier("a", lineno=1)], lineno=1)],
                                   lineno=1), lineno=1), lineno=1)], lineno=1),
                                  1)}, lineno=1)),
        ("foo(){if(a > b){a += 1;} elif(c and d){e += 1;} elif(d or f){e = 1;} else{print(a);}}",
         Program({"foo": Function(Identifier("foo", lineno=1), [], Block([
             IfStatement(GreaterExpr(Identifier("a", lineno=1), Identifier("b", lineno=1), lineno=1),
                         Block([AddAssignment(Identifier("a", lineno=1), Integer(1, lineno=1), lineno=1)], lineno=1),
                         [ElifBlock(AndExpr(Identifier("c", lineno=1), Identifier("d", lineno=1), lineno=1),
                                    Block([AddAssignment(Identifier("e", lineno=1), Integer(1, lineno=1), lineno=1)],
                                          lineno=1), lineno=1),
                          ElifBlock(OrExpr(Identifier("d", lineno=1), Identifier("f", lineno=1), lineno=1),
                                    Block([BasicAssignment(Identifier("e", lineno=1), Integer(1, lineno=1), lineno=1)],
                                          lineno=1), lineno=1)],
                         ElseBlock(
                             Block([FunCall(Identifier("print", lineno=1), [Identifier("a", lineno=1)], lineno=1)],
                                   lineno=1), lineno=1), lineno=1)], lineno=1),
                                  1)}, lineno=1)),
    ])
    def test_try_parse_else_block(self, case, expect):
        # GIVEN
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(error_handler)

        # WHEN
        program = parser.parse(lexer)

        # THEN
        self.assertEqual(expect, program, f"Else statement not parsed: {case}")

    @parameterized.expand([
        ("foo(){for(a in b)print(a);}",
         Program({"foo": Function(Identifier("foo", lineno=1), [], Block([
             ForStatement(Identifier("a", lineno=1), Identifier("b", lineno=1),
                          Block([FunCall(Identifier("print", lineno=1), [Identifier("a", lineno=1)], lineno=1)],
                                lineno=1), lineno=1)], lineno=1), lineno=1)}, lineno=1)),
        ("foo(){for(a in b){print(a);}}",
         Program({"foo": Function(Identifier("foo", lineno=1), [], Block([
             ForStatement(Identifier("a", lineno=1), Identifier("b", lineno=1),
                          Block([FunCall(Identifier("print", lineno=1), [Identifier("a", lineno=1)], lineno=1)],
                                lineno=1), lineno=1)], lineno=1), lineno=1)}, lineno=1)),
    ])
    def test_try_parse_for_statement(self, case, expect):
        # GIVEN
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(error_handler)

        # WHEN
        program = parser.parse(lexer)

        # THEN
        self.assertEqual(expect, program, f"For statement not parsed: {case}")

    @parameterized.expand([
        ("foo(){while(a and b)print(a);}",
         Program({"foo": Function(Identifier("foo", lineno=1), [], Block([
             WhileStatement(AndExpr(Identifier("a", lineno=1), Identifier("b", lineno=1), lineno=1),
                            Block([FunCall(Identifier("print", lineno=1), [Identifier("a", lineno=1)], lineno=1)],
                                  lineno=1), lineno=1)], lineno=1), lineno=1)}, lineno=1)),
        ("foo(){while(true){print(a);}}",
         Program({"foo": Function(Identifier("foo", lineno=1), [], Block([
             WhileStatement(Boolean(True, lineno=1),
                            Block([FunCall(Identifier("print", lineno=1), [Identifier("a", lineno=1)], lineno=1)],
                                  lineno=1), lineno=1)], lineno=1), lineno=1)}, lineno=1)),
    ])
    def test_try_parse_while_statement(self, case, expect):
        # GIVEN
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(error_handler)

        # WHEN
        program = parser.parse(lexer)

        # THEN
        self.assertEqual(expect, program, f"While statement not parsed: {case}")

    @parameterized.expand([
        ("foo(){a = -a and b or c - 2 * 3 and (b or not g);}",
         Program({"foo": Function(Identifier("foo", lineno=1), [], Block([
             BasicAssignment(
                 Identifier("a", lineno=1),
                 OrExpr(AndExpr(InvertExpr(Identifier("a", lineno=1)), Identifier("b", lineno=1), lineno=1),
                        AndExpr(
                            SubExpr(Identifier("c", lineno=1),
                                    MulExpr(Integer(2, lineno=1), Integer(3, lineno=1), lineno=1), lineno=1),
                            OrExpr(Identifier("b", lineno=1), Negate(Identifier("g", lineno=1), lineno=1), lineno=1),
                            lineno=1), lineno=1), lineno=1)], lineno=1), lineno=1)}, lineno=1)),
    ])
    def test_try_parse_expression(self, case, expect):
        # GIVEN
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(error_handler)

        # WHEN
        program = parser.parse(lexer)

        # THEN
        self.assertEqual(expect, program, f"Expression not parsed: {case}")

    @parameterized.expand([
        ("foo(){a = c or b;}",
         Program({"foo": Function(Identifier("foo", lineno=1), [], Block(
             [BasicAssignment(Identifier("a", lineno=1),
                              OrExpr(Identifier("c", lineno=1), Identifier("b", lineno=1), lineno=1), lineno=1)],
             lineno=1), lineno=1)}, lineno=1)),
    ])
    def test_try_parse_or_expr(self, case, expect):
        # GIVEN
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(error_handler)

        # WHEN
        program = parser.parse(lexer)

        # THEN
        self.assertEqual(expect, program, f"Or expression not parsed: {case}")

    @parameterized.expand([
        ("foo(){a = c and b;}",
         Program({"foo": Function(Identifier("foo", lineno=1), [], Block([BasicAssignment(Identifier("a", lineno=1),
                                                                                          AndExpr(
                                                                                              Identifier("c", lineno=1),
                                                                                              Identifier("b", lineno=1),
                                                                                              lineno=1), lineno=1)],
                                                                         1), lineno=1)}, lineno=1)),
    ])
    def test_try_parse_and_expr(self, case, expect):
        # GIVEN
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(error_handler)

        # WHEN
        program = parser.parse(lexer)

        # THEN
        self.assertEqual(expect, program, f"And expression not parsed: {case}")

    @parameterized.expand([
        ("foo(){a = not b;}",
         Program({"foo": Function(Identifier("foo", lineno=1), [],
                                  Block([BasicAssignment(Identifier("a", lineno=1),
                                                         Negate(Identifier("b", lineno=1), lineno=1), lineno=1)],
                                        lineno=1),
                                  1)}, lineno=1)),
    ])
    def test_try_parse_negate_expr(self, case, expect):
        # GIVEN
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(error_handler)

        # WHEN
        program = parser.parse(lexer)

        # THEN
        self.assertEqual(expect, program, f"Negate expression not parsed: {case}")

    @parameterized.expand([
        ("foo(){a = b == c;}", Program({"foo": Function(Identifier("foo", lineno=1), [], Block([
            BasicAssignment(Identifier("a", lineno=1),
                            EqExpr(Identifier("b", lineno=1), Identifier("c", lineno=1), lineno=1), lineno=1)],
            lineno=1), lineno=1)}, lineno=1)),
        ("foo(){a = b != c;}", Program({"foo": Function(Identifier("foo", lineno=1), [], Block([
            BasicAssignment(Identifier("a", lineno=1),
                            NotEqExpr(Identifier("b", lineno=1), Identifier("c", lineno=1), lineno=1), lineno=1)],
            lineno=1), lineno=1)}, lineno=1)),
        ("foo(){a = b > c;}", Program({"foo": Function(Identifier("foo", lineno=1), [], Block([
            BasicAssignment(Identifier("a", lineno=1),
                            GreaterExpr(Identifier("b", lineno=1), Identifier("c", lineno=1), lineno=1), lineno=1)],
            lineno=1), lineno=1)},
                                      1)),
        ("foo(){a = b < c;}", Program({"foo": Function(Identifier("foo", lineno=1), [], Block([
            BasicAssignment(Identifier("a", lineno=1),
                            LessExpr(Identifier("b", lineno=1), Identifier("c", lineno=1), lineno=1), lineno=1)],
            lineno=1), lineno=1)}, lineno=1)),
        ("foo(){a = b >= c;}", Program({"foo": Function(Identifier("foo", lineno=1), [], Block([
            BasicAssignment(Identifier("a", lineno=1),
                            GreaterEqExpr(Identifier("b", lineno=1), Identifier("c", lineno=1), lineno=1), lineno=1)],
            lineno=1), lineno=1)},
                                       1)),
        ("foo(){a = b <= c;}", Program({"foo": Function(Identifier("foo", lineno=1), [], Block([
            BasicAssignment(Identifier("a", lineno=1),
                            LessEqExpr(Identifier("b", lineno=1), Identifier("c", lineno=1), lineno=1), lineno=1)],
            lineno=1), lineno=1)},
                                       1)),
        ("foo(){a = b in c;}", Program({"foo": Function(Identifier("foo", lineno=1), [], Block([
            BasicAssignment(Identifier("a", lineno=1),
                            InExpr(Identifier("b", lineno=1), Identifier("c", lineno=1), lineno=1), lineno=1)],
            lineno=1), lineno=1)}, lineno=1)),
    ])
    def test_try_parse_comp_expr(self, case, expect):
        # GIVEN
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(error_handler)

        # WHEN
        program = parser.parse(lexer)

        # THEN
        self.assertEqual(expect, program, f"Comp expression not parsed: {case}")

    @parameterized.expand([
        ("foo(){a = b + c;}", Program({"foo": Function(Identifier("foo", lineno=1), [], Block([
            BasicAssignment(Identifier("a", lineno=1),
                            AddExpr(Identifier("b", lineno=1), Identifier("c", lineno=1), lineno=1), lineno=1)],
            lineno=1), lineno=1)}, lineno=1)),
        ("foo(){a = b - c;}", Program({"foo": Function(Identifier("foo", lineno=1), [], Block([
            BasicAssignment(Identifier("a", lineno=1),
                            SubExpr(Identifier("b", lineno=1), Identifier("c", lineno=1), lineno=1), lineno=1)],
            lineno=1), lineno=1)}, lineno=1)),
        ("foo(){a = b + c - d;}", Program({"foo": Function(Identifier("foo", lineno=1), [], Block([
            BasicAssignment(Identifier("a", lineno=1),
                            SubExpr(AddExpr(Identifier("b", lineno=1), Identifier("c", lineno=1), lineno=1),
                                    Identifier("d", lineno=1), lineno=1), lineno=1)], lineno=1),
                                                           1)}, lineno=1)),
    ])
    def test_try_parse_sum_expr(self, case, expect):
        # GIVEN
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(error_handler)

        # WHEN
        program = parser.parse(lexer)

        # THEN
        self.assertEqual(expect, program, f"Sum expression not parsed: {case}")

    @parameterized.expand([
        ("foo(){a = b * c;}", Program({"foo": Function(Identifier("foo", lineno=1), [], Block([
            BasicAssignment(Identifier("a", lineno=1),
                            MulExpr(Identifier("b", lineno=1), Identifier("c", lineno=1), lineno=1), lineno=1)],
            lineno=1), lineno=1)}, lineno=1)),
        ("foo(){a = b / c;}", Program({"foo": Function(Identifier("foo", lineno=1), [], Block([
            BasicAssignment(Identifier("a", lineno=1),
                            DivExpr(Identifier("b", lineno=1), Identifier("c", lineno=1), lineno=1), lineno=1)],
            lineno=1), lineno=1)}, lineno=1)),
        ("foo(){a = b % c;}", Program({"foo": Function(Identifier("foo", lineno=1), [], Block([
            BasicAssignment(Identifier("a", lineno=1),
                            ModExpr(Identifier("b", lineno=1), Identifier("c", lineno=1), lineno=1), lineno=1)],
            lineno=1), lineno=1)}, lineno=1)),
        ("foo(){a = b // c;}", Program({"foo": Function(Identifier("foo", lineno=1), [], Block([
            BasicAssignment(Identifier("a", lineno=1),
                            IntDivExpr(Identifier("b", lineno=1), Identifier("c", lineno=1), lineno=1), lineno=1)],
            lineno=1), lineno=1)},
                                       1)),
    ])
    def test_try_parse_mul_expr(self, case, expect):
        # GIVEN
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(error_handler)

        # WHEN
        program = parser.parse(lexer)

        # THEN
        self.assertEqual(expect, program, f"Mul expression not parsed: {case}")

    @parameterized.expand([
        ("foo(){a = b.c;}", Program({"foo": Function(Identifier("foo", lineno=1), [], Block([
            BasicAssignment(Identifier("a", lineno=1),
                            DotOperator(Identifier("b", lineno=1), Identifier("c", lineno=1), lineno=1), lineno=1)],
            lineno=1), lineno=1)},
                                    1)),
    ])
    def test_try_parse_dot_operator(self, case, expect):
        # GIVEN
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(error_handler)

        # WHEN
        program = parser.parse(lexer)

        # THEN
        self.assertEqual(expect, program, f"Dot operator not parsed: {case}")

    @parameterized.expand([
        ("foo(){a = b();}", Program({"foo": Function(Identifier("foo", lineno=1), [], Block([
            BasicAssignment(Identifier("a", lineno=1), FunCall(Identifier("b", lineno=1), [], lineno=1), lineno=1)],
            lineno=1), lineno=1)}, lineno=1)),
    ])
    def test_try_parse_fun_call(self, case, expect):
        # GIVEN
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(error_handler)

        # WHEN
        program = parser.parse(lexer)

        # THEN
        self.assertEqual(expect, program, f"Function call not parsed: {case}")

    @parameterized.expand([
        ("foo(){a = b(a, b, 5);}", Program({"foo": Function(Identifier("foo", lineno=1), [], Block([
            BasicAssignment(Identifier("a", lineno=1),
                            FunCall(Identifier("b", lineno=1),
                                    [Identifier("a", lineno=1), Identifier("b", lineno=1), Integer(5, lineno=1)],
                                    lineno=1), lineno=1)
        ], lineno=1), lineno=1)}, lineno=1)),
    ])
    def test_try_parse_arguments(self, case, expect):
        # GIVEN
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(error_handler)

        # WHEN
        program = parser.parse(lexer)

        # THEN
        self.assertEqual(expect, program, f"Function arguments not parsed: {case}")

    @parameterized.expand([
        ("foo(){a = b[1];}", Program({"foo": Function(Identifier("foo", lineno=1), [], Block([
            BasicAssignment(Identifier("a", lineno=1),
                            ListElement(Identifier("b", lineno=1), Integer(1, lineno=1), lineno=1), lineno=1)],
            lineno=1), lineno=1)}, lineno=1)),
    ])
    def test_try_parse_list_element(self, case, expect):
        # GIVEN
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(error_handler)

        # WHEN
        program = parser.parse(lexer)

        # THEN
        self.assertEqual(expect, program, f"List element not parsed: {case}")

    @parameterized.expand([
        ("foo(){a = (a - 5) * 2;}",
         Program({"foo": Function(Identifier("foo", lineno=1), [], Block([
             BasicAssignment(Identifier("a", lineno=1),
                             MulExpr(SubExpr(Identifier("a", lineno=1), Integer(5, lineno=1), lineno=1),
                                     Integer(2, lineno=1), lineno=1), lineno=1)], lineno=1), lineno=1)},
                 1)),
    ])
    def test_try_parse_parenthesis(self, case, expect):
        # GIVEN
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(error_handler)

        # WHEN
        program = parser.parse(lexer)

        # THEN
        self.assertEqual(expect, program, f"Parenthesis not parsed: {case}")

    @parameterized.expand([
        ("foo(){a = [1, 2, 3];}",
         Program({"foo": Function(Identifier("foo", lineno=1), [], Block([
             BasicAssignment(Identifier("a", lineno=1),
                             List([Integer(1, lineno=1), Integer(2, lineno=1), Integer(3, lineno=1)], lineno=1),
                             lineno=1)], lineno=1), lineno=1)},
                 1)),
        ("foo(){a = [];}",
         Program({"foo": Function(Identifier("foo", lineno=1), [], Block([
             BasicAssignment(Identifier("a", lineno=1), List([], lineno=1), lineno=1)], lineno=1), lineno=1)},
                 lineno=1)),
    ])
    def test_try_parse_list(self, case, expect):
        # GIVEN
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(error_handler)

        # WHEN
        program = parser.parse(lexer)

        # THEN
        self.assertEqual(expect, program, f"List not parsed: {case}")

    @parameterized.expand([
        ("foo(){a = \"test\";}",
         Program({"foo": Function(Identifier("foo", lineno=1), [], Block([
             BasicAssignment(Identifier("a", lineno=1), String("test", lineno=1), lineno=1)], lineno=1), lineno=1)},
                 lineno=1)),
        ("foo(){a = 'test';}",
         Program({"foo": Function(Identifier("foo", lineno=1), [], Block([
             BasicAssignment(Identifier("a", lineno=1), String("test", lineno=1), lineno=1)], lineno=1), lineno=1)},
                 lineno=1)),
        ("foo(){a = 25;}",
         Program({"foo": Function(Identifier("foo", lineno=1), [], Block([
             BasicAssignment(Identifier("a", lineno=1), Integer(25, lineno=1), lineno=1)], lineno=1), lineno=1)},
                 lineno=1)),
        ("foo(){a = true;}",
         Program({"foo": Function(Identifier("foo", lineno=1), [], Block([
             BasicAssignment(Identifier("a", lineno=1), Boolean(True, lineno=1), lineno=1)], lineno=1), lineno=1)},
                 lineno=1)),
        ("foo(){a = false;}",
         Program({"foo": Function(Identifier("foo", lineno=1), [], Block([
             BasicAssignment(Identifier("a", lineno=1), Boolean(False, lineno=1), lineno=1)], lineno=1), lineno=1)},
                 lineno=1)),
        ("foo(){a = null;}",
         Program({"foo": Function(Identifier("foo", lineno=1), [], Block([
             BasicAssignment(Identifier("a", lineno=1), Null(1), lineno=1)], lineno=1), lineno=1)}, lineno=1)),
    ])
    def test_try_parse_atom(self, case, expect):
        # GIVEN
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(error_handler)

        # WHEN
        program = parser.parse(lexer)

        # THEN
        self.assertEqual(expect, program, f"Atom not parsed: {case}")


def get_error_handler():
    return ErrorHandler(module="test_parser", level=logging.CRITICAL)


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
         MissingRightSquareBracketException),
        ("foo(){[a}",
         MissingRightSquareBracketException),
        ("foo(){a[}",
         MissingRightSquareBracketException),
        ("foo(){a[1}",
         MissingRightSquareBracketException),
    ])
    def test_detect_missing_brackets(self, case, expect):
        # GIVEN
        # error_handler = ErrorHandler(logging.CRITICAL)
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(error_handler)

        # THEN
        self.assertRaises(expect, parser.parse, lexer)

    @parameterized.expand([
        ("foo()",
         MissingFunctionBlockException),
        ("foo(){}boo()",
         MissingFunctionBlockException),
    ])
    def test_detect_missing_function_body(self, case, expect):
        # GIVEN
        # error_handler = ErrorHandler(logging.CRITICAL)
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(error_handler)

        # THEN
        self.assertRaises(expect, parser.parse, lexer)

    @parameterized.expand([
        ("foo(){}foo(){}",
         FunctionRedefinitionException),
        ("foo(){}boo(){}foo(){}",
         FunctionRedefinitionException),
    ])
    def test_detect_function_redefinition(self, case, expect):
        # GIVEN
        # error_handler = ErrorHandler(logging.CRITICAL)
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(error_handler)

        # THEN
        self.assertRaises(expect, parser.parse, lexer)

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
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(error_handler)

        # THEN
        self.assertRaises(expect, parser.parse, lexer)

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
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(error_handler)

        # THEN
        self.assertRaises(expect, parser.parse, lexer)

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
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(error_handler)

        # THEN
        self.assertRaises(expect, parser.parse, lexer)

    @parameterized.expand([
        ("foo(){a = }",
         MissingRightSideOfAssignmentException),
    ])
    def test_detect_missing_expression_after_comma(self, case, expect):
        # GIVEN
        # error_handler = ErrorHandler(logging.CRITICAL)
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(error_handler)

        # THEN
        self.assertRaises(expect, parser.parse, lexer)

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
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(error_handler)

        # THEN
        self.assertRaises(expect, parser.parse, lexer)

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
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(error_handler)

        # THEN
        self.assertRaises(expect, parser.parse, lexer)

    @parameterized.expand([
        ("foo(){for()}",
         MissingIteratorException),
    ])
    def test_detect_missing_iterator(self, case, expect):
        # GIVEN
        # error_handler = ErrorHandler(logging.CRITICAL)
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(error_handler)

        # THEN
        self.assertRaises(expect, parser.parse, lexer)

    @parameterized.expand([
        ("foo(){for(a)}",
         MissingKeywordInException),
    ])
    def test_detect_missing_in_keyword(self, case, expect):
        # GIVEN
        # error_handler = ErrorHandler(logging.CRITICAL)
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(error_handler)

        # THEN
        self.assertRaises(expect, parser.parse, lexer)

    @parameterized.expand([
        ("foo(){for(a in)}",
         MissingIterableException),
    ])
    def test_detect_missing_iterable(self, case, expect):
        # GIVEN
        # error_handler = ErrorHandler(logging.CRITICAL)
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(error_handler)

        # THEN
        self.assertRaises(expect, parser.parse, lexer)

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
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(error_handler)

        # THEN
        self.assertRaises(expect, parser.parse, lexer)

    @parameterized.expand([
        ("foo(){a.}",
         MissingIdentifierAfterDotException),
    ])
    def test_detect_missing_identifier_after_dot(self, case, expect):
        # GIVEN
        # error_handler = ErrorHandler(logging.CRITICAL)
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(case), error_handler)
        parser = Parser(error_handler)

        # THEN
        self.assertRaises(expect, parser.parse, lexer)


class TestParserClasses(unittest.TestCase):
    @parameterized.expand([
        (Identifier("a", lineno=1),),
        (Null(1),),
        (String("test", lineno=1),),
        (Atom(String("a", lineno=1), lineno=1),),
        (FunCall(Identifier("print", lineno=1), List([Integer(2, lineno=1)], lineno=1), lineno=1),),
        (TwoSidedExpression(Identifier("a", lineno=1), Integer(2, lineno=1), lineno=1),),
        (Block([FunCall(Identifier("print", lineno=1), List([Integer(2, lineno=1)], lineno=1), lineno=1)], lineno=1),),
        (
                WhileStatement(Boolean(True, lineno=1),
                               Block([FunCall(Identifier("print", lineno=1), List([Integer(2, lineno=1)], lineno=1),
                                              lineno=1)], lineno=1), lineno=1),),
        (ForStatement(Identifier("a", lineno=1), Identifier("a", lineno=1),
                      Block([FunCall(Identifier("print", lineno=1), List([Integer(2, lineno=1)], lineno=1), lineno=1)],
                            lineno=1), lineno=1),),
        (IfStatement(Boolean(True, lineno=1),
                     Block([FunCall(Identifier("print", lineno=1), List([Integer(2, lineno=1)], lineno=1), lineno=1)],
                           lineno=1),
                     [ElifBlock(Boolean(True, lineno=1),
                                Block([FunCall(Identifier("print", lineno=1), List([Integer(2, lineno=1)], lineno=1),
                                               lineno=1)], lineno=1), lineno=1)],
                     ElseBlock(Block(
                         [FunCall(Identifier("print", lineno=1), List([Integer(2, lineno=1)], lineno=1), lineno=1)],
                         lineno=1), lineno=1), lineno=1),),
        (ReturnStatement([Identifier("a", lineno=1)], lineno=1),),
        (Assignment(Identifier("a", lineno=1), Integer(2, lineno=1), lineno=1),),
        (
                Function(Identifier("a", lineno=1), [Identifier("b", lineno=1)],
                         Block([Assignment(Identifier("a", lineno=1), Integer(2, lineno=1), lineno=1)], lineno=1),
                         1),),
        (Program(
            {"a": Function(Identifier("a", lineno=1), [Identifier("b", lineno=1)],
                           Block([Assignment(Identifier("a", lineno=1), Integer(2, lineno=1), lineno=1)], lineno=1),
                           lineno=1)}, lineno=1),),
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
        (Atom(String("a", lineno=1), lineno=1),),
        (TwoSidedExpression(Identifier("a", lineno=1), Integer(2, lineno=1), lineno=1),),
        (
                WhileStatement(Boolean(True, lineno=1), Block(
                    [FunCall(Identifier("print", lineno=1), List([Integer(2, lineno=1)], lineno=1), lineno=1)],
                    lineno=1), lineno=1),),
        (ForStatement(Identifier("a", lineno=1), Identifier("a", lineno=1),
                      Block([FunCall(Identifier("print", lineno=1), List([Integer(2, lineno=1)], lineno=1), lineno=1)],
                            lineno=1), lineno=1),),
        (IfStatement(Boolean(True, lineno=1),
                     Block([FunCall(Identifier("print", lineno=1), List([Integer(2, lineno=1)], lineno=1), lineno=1)],
                           lineno=1), [], None,
                     lineno=1),),
        (ElifBlock(Boolean(True, lineno=1),
                   Block([FunCall(Identifier("print", lineno=1), List([Integer(2, lineno=1)], lineno=1), lineno=1)],
                         lineno=1), lineno=1),),
        (ElseBlock(
            Block([FunCall(Identifier("print", lineno=1), List([Integer(2, lineno=1)], lineno=1), lineno=1)], lineno=1),
            lineno=1),),
        (ReturnStatement([Identifier("a", lineno=1)], lineno=1),),
        (Assignment(Identifier("a", lineno=1), Integer(2, lineno=1), lineno=1),),
        (
                Function(Identifier("a", lineno=1), [Identifier("b", lineno=1)],
                         Block([Assignment(Identifier("a", lineno=1), Integer(2, lineno=1), lineno=1)], lineno=1),
                         1),),
        (Program(
            {"a": Function(Identifier("a", lineno=1), [Identifier("b", lineno=1)],
                           Block([Assignment(Identifier("a", lineno=1), Integer(2, lineno=1), lineno=1)], lineno=1),
                           lineno=1)}, lineno=1),),
    ])
    def test_check_objects_equality(self, case):
        self.assertEqual(case, case, f"Class {case.__class__} has wrong __eq__.")

    @parameterized.expand([
        (Atom(String("a", lineno=1), lineno=1),
         Atom(String("b", lineno=1), lineno=1)),
        (TwoSidedExpression(Identifier("a", lineno=1), Integer(2, lineno=1), lineno=1),
         TwoSidedExpression(Identifier("b", lineno=1), Integer(2, lineno=1), lineno=1)),
        (TwoSidedExpression(Identifier("a", lineno=1), Integer(2, lineno=1), lineno=1),
         TwoSidedExpression(Identifier("a", lineno=1), Integer(1, lineno=1), lineno=1)),
        (WhileStatement(Boolean(True, lineno=1), Block(
            [FunCall(Identifier("print", lineno=1), List([Integer(2, lineno=1)], lineno=1), lineno=1)], lineno=1),
                        lineno=1),
         WhileStatement(Boolean(False, lineno=1), Block(
             [FunCall(Identifier("print", lineno=1), List([Integer(2, lineno=1)], lineno=1), lineno=1)], lineno=1),
                        lineno=1)),
        (WhileStatement(Boolean(True, lineno=1), Block(
            [FunCall(Identifier("print", lineno=1), List([Integer(2, lineno=1)], lineno=1), lineno=1)], lineno=1),
                        lineno=1),
         WhileStatement(Boolean(True, lineno=1),
                        Block([TwoSidedExpression(Identifier("a", lineno=1), Integer(2, lineno=1), lineno=1)],
                              lineno=1),
                        lineno=1)),
        (ForStatement(Identifier("a", lineno=1), Identifier("a", lineno=1),
                      Block([FunCall(Identifier("print", lineno=1), List([Integer(2, lineno=1)], lineno=1), lineno=1)],
                            lineno=1), lineno=1),
         ForStatement(Identifier("b", lineno=1), Identifier("a", lineno=1),
                      Block([FunCall(Identifier("print", lineno=1), List([Integer(2, lineno=1)], lineno=1), lineno=1)],
                            lineno=1), lineno=1)),
        (ForStatement(Identifier("a", lineno=1), Identifier("a", lineno=1),
                      Block([FunCall(Identifier("print", lineno=1), List([Integer(2, lineno=1)], lineno=1), lineno=1)],
                            lineno=1), lineno=1),
         ForStatement(Identifier("a", lineno=1), Identifier("b", lineno=1),
                      Block([FunCall(Identifier("print", lineno=1), List([Integer(2, lineno=1)], lineno=1), lineno=1)],
                            lineno=1), lineno=1)),
        (ForStatement(Identifier("a", lineno=1), Identifier("a", lineno=1),
                      Block([FunCall(Identifier("print", lineno=1), List([Integer(2, lineno=1)], lineno=1), lineno=1)],
                            lineno=1), lineno=1),
         ForStatement(Identifier("a", lineno=1), Identifier("a", lineno=1),
                      Block([TwoSidedExpression(Identifier("a", lineno=1), Integer(2, lineno=1), lineno=1)], lineno=1),
                      lineno=1)),
        (IfStatement(Boolean(True, lineno=1),
                     Block([FunCall(Identifier("print", lineno=1), List([Integer(2, lineno=1)], lineno=1), lineno=1)],
                           lineno=1), [], None, lineno=1),
         IfStatement(Boolean(False, lineno=1),
                     Block([FunCall(Identifier("print", lineno=1), List([Integer(2, lineno=1)], lineno=1), lineno=1)],
                           lineno=1), [], None, lineno=1)),
        (IfStatement(Boolean(True, lineno=1),
                     Block([FunCall(Identifier("print", lineno=1), List([Integer(2, lineno=1)], lineno=1), lineno=1)],
                           lineno=1), [], None, lineno=1),
         IfStatement(Boolean(True, lineno=1),
                     Block([TwoSidedExpression(Identifier("a", lineno=1), Integer(2, lineno=1), lineno=1)], lineno=1),
                     [], None, lineno=1)),
        (IfStatement(Boolean(True, lineno=1),
                     Block([FunCall(Identifier("print", lineno=1), List([Integer(2, lineno=1)], lineno=1), lineno=1)],
                           lineno=1), [], None, lineno=1),
         IfStatement(Boolean(True, lineno=1),
                     Block([FunCall(Identifier("print", lineno=1), List([Integer(2, lineno=1)], lineno=1), lineno=1)],
                           lineno=1),
                     [ElifBlock(Boolean(True, lineno=1), Block(
                         [FunCall(Identifier("print", lineno=1), List([Integer(2, lineno=1)], lineno=1), lineno=1)],
                         lineno=1), lineno=1)], None, lineno=1)),
        (IfStatement(Boolean(True, lineno=1),
                     Block([FunCall(Identifier("print", lineno=1), List([Integer(2, lineno=1)], lineno=1), lineno=1)],
                           lineno=1),
                     [ElifBlock(Boolean(False, lineno=1), Block(
                         [FunCall(Identifier("print", lineno=1), List([Integer(2, lineno=1)], lineno=1), lineno=1)],
                         lineno=1), lineno=1)], None, lineno=1),
         IfStatement(Boolean(True, lineno=1),
                     Block([FunCall(Identifier("print", lineno=1), List([Integer(2, lineno=1)], lineno=1), lineno=1)],
                           lineno=1),
                     [ElifBlock(Boolean(True, lineno=1), Block(
                         [FunCall(Identifier("print", lineno=1), List([Integer(2, lineno=1)], lineno=1), lineno=1)],
                         lineno=1), lineno=1)], None, lineno=1)),
        (IfStatement(Boolean(True, lineno=1),
                     Block([FunCall(Identifier("print", lineno=1), List([Integer(2, lineno=1)], lineno=1), lineno=1)],
                           lineno=1), [], None, lineno=1),
         IfStatement(Boolean(True, lineno=1),
                     Block([FunCall(Identifier("print", lineno=1), List([Integer(2, lineno=1)], lineno=1), lineno=1)],
                           lineno=1), [],
                     ElseBlock(Block(
                         [FunCall(Identifier("print", lineno=1), List([Integer(2, lineno=1)], lineno=1), lineno=1)],
                         lineno=1), lineno=1), lineno=1)),
        (IfStatement(Boolean(True, lineno=1),
                     Block([FunCall(Identifier("print", lineno=1), List([Integer(2, lineno=1)], lineno=1), lineno=1)],
                           lineno=1), [],
                     ElseBlock(Block(
                         [FunCall(Identifier("input", lineno=1), List([String("test", lineno=1)], lineno=1), lineno=1)],
                         lineno=1), lineno=1), lineno=1),
         IfStatement(Boolean(True, lineno=1),
                     Block([FunCall(Identifier("print", lineno=1), List([Integer(2, lineno=1)], lineno=1), lineno=1)],
                           lineno=1), [],
                     ElseBlock(Block(
                         [FunCall(Identifier("print", lineno=1), List([Integer(2, lineno=1)], lineno=1), lineno=1)],
                         lineno=1), lineno=1), lineno=1)),
        (ElifBlock(Boolean(True, lineno=1),
                   Block([FunCall(Identifier("print", lineno=1), List([Integer(2, lineno=1)], lineno=1), lineno=1)],
                         lineno=1), lineno=1),
         ElifBlock(Boolean(False, lineno=1),
                   Block([FunCall(Identifier("print", lineno=1), List([Integer(2, lineno=1)], lineno=1), lineno=1)],
                         lineno=1), lineno=1)),
        (ElifBlock(Boolean(True, lineno=1),
                   Block([FunCall(Identifier("print", lineno=1), List([Integer(2, lineno=1)], lineno=1), lineno=1)],
                         lineno=1), lineno=1),
         ElifBlock(Boolean(True, lineno=1),
                   Block([TwoSidedExpression(Identifier("a", lineno=1), Integer(2, lineno=1), lineno=1)], lineno=1),
                   lineno=1)),
        (ElseBlock(
            Block([FunCall(Identifier("print", lineno=1), List([Integer(2, lineno=1)], lineno=1), lineno=1)], lineno=1),
            lineno=1),
         ElseBlock(Block([TwoSidedExpression(Identifier("a", lineno=1), Integer(2, lineno=1), lineno=1)], lineno=1),
                   lineno=1)),
        (ReturnStatement([Identifier("a", lineno=1)], lineno=1),
         ReturnStatement([Identifier("b", lineno=1)], lineno=1)),
        (Assignment(Identifier("a", lineno=1), Integer(2, lineno=1), lineno=1),
         Assignment(Identifier("b", lineno=1), Integer(2, lineno=1), lineno=1)),
        (Assignment(Identifier("a", lineno=1), Integer(2, lineno=1), lineno=1),
         Assignment(Identifier("a", lineno=1), Integer(1, lineno=1), lineno=1)),
        (Function(Identifier("a", lineno=1), [Identifier("b", lineno=1)],
                  Block([Assignment(Identifier("a", lineno=1), Integer(2, lineno=1), lineno=1)], lineno=1), lineno=1),
         Function(Identifier("b", lineno=1), [Identifier("b", lineno=1)],
                  Block([Assignment(Identifier("a", lineno=1), Integer(2, lineno=1), lineno=1)], lineno=1), lineno=1)),
        (Function(Identifier("a", lineno=1), [Identifier("b", lineno=1)],
                  Block([Assignment(Identifier("a", lineno=1), Integer(2, lineno=1), lineno=1)], lineno=1), lineno=1),
         Function(Identifier("a", lineno=1), [Identifier("c", lineno=1)],
                  Block([Assignment(Identifier("a", lineno=1), Integer(2, lineno=1), lineno=1)], lineno=1), lineno=1)),
        (Function(Identifier("a", lineno=1), [Identifier("b", lineno=1)],
                  Block([Assignment(Identifier("a", lineno=1), Integer(2, lineno=1), lineno=1)], lineno=1), lineno=1),
         Function(Identifier("a", lineno=1), [Identifier("b", lineno=1)],
                  Block([FunCall(Identifier("print", lineno=1), List([Integer(2, lineno=1)], lineno=1), lineno=1)],
                        lineno=1), lineno=1)),
        (Program({"a": Function(Identifier("a", lineno=1), [Identifier("b", lineno=1)],
                                Block([Assignment(Identifier("a", lineno=1), Integer(2, lineno=1), lineno=1)],
                                      lineno=1), lineno=1)}, lineno=1),
         Program(
             {"b": Function(Identifier("b", lineno=1), [Identifier("b", lineno=1)],
                            Block([Assignment(Identifier("a", lineno=1), Integer(2, lineno=1), lineno=1)], lineno=1),
                            lineno=1)}, lineno=1)),
    ])
    def test_check_objects_inequality(self, case, compare):
        self.assertNotEqual(compare, case, f"Class {case.__class__} has wrong __eq__.")


def suite():
    suite_ = unittest.TestSuite()
    suite_.addTest(unittest.makeSuite(TestParser, 'test'))
    suite_.addTest(unittest.makeSuite(TestParserErrorHandling, 'test'))
    suite_.addTest(unittest.makeSuite(TestParserClasses, 'test'))
    return suite_
