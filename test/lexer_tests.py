import logging
import unittest
from io import StringIO

from parameterized import parameterized

from ErrorHandlerModule.ErrorHandler import ErrorHandler
from ErrorHandlerModule.ErrorType import IdentifierTooLongLexerException, TextConstTooLongLexerException, CommentTooLongLexerException, \
    UnknownTokenLexerException, UnterminatedStringLexerException, MAX_COMMENT_LENGTH, MAX_IDENTIFIER_LENGTH, IntegerTooLargeLexerException, \
    MAX_TEXT_CONST_LENGTH
from LexerModule.Lexer import Lexer, Token, TokenType, keywords
from LexerModule.Tokens import operators


class TestLexerSimple(unittest.TestCase):
    def test_try_build_etx(self):
        # GIVEN
        source = "\x03"
        expected = Token(TokenType.T_ETX, '\x03', 1, 1)
        lex = Lexer(StringIO(source), ErrorHandler())

        # WHEN
        token = lex.get_next_token()

        # THEN
        self.assertEqual(expected, token, "ETX not detected correctly.")

    @parameterized.expand([
        ("# test1", " test1"),
        ("#    test 2", "    test 2"),
        ("#test 3\n test3", "test 3"),
    ])
    def test_try_build_comment(self, case, expect):
        # GIVEN
        source = case
        expected = Token(TokenType.T_COMMENT, expect, 1, 1)
        lex = Lexer(StringIO(source), ErrorHandler())

        # WHEN
        token = lex.get_next_token()

        # THEN
        self.assertEqual(expected, token, "Comment not detected correctly.")

    @parameterized.expand([
        ("test1", "test1"),
        ("test2    ", "test2"),
        ("test_3", "test_3"),
        ("_test_4\n test4", "_test_4"),
        ("__test_4\n __test4", "__test_4"),
        ("while1", "while1"),
        ("_if", "_if"),
        ("forfor", "forfor"),
    ])
    def test_try_build_identifier(self, case, expect):
        # GIVEN
        source = case
        expected = Token(TokenType.T_IDENTIFIER, expect, 1, 1)
        lex = Lexer(StringIO(source), ErrorHandler())

        # WHEN
        token = lex.get_next_token()

        # THEN
        self.assertEqual(expected, token, "Identifier not detected correctly.")

    @parameterized.expand([
        ("if ", "if"),
        ("elif", "elif"),
        ("else\n", "else"),
        ("for\t", "for"),
        ("while|", "while"),
        ("return   ", "return"),
        ("and 12", "and"),
        ("or\n\n", "or"),
        ("in", "in"),
        ("not\n", "not"),
        ("true", "true"),
        ("false", "false"),
        ("null", "null"),
    ])
    def test_try_build_keyword(self, case, expect):
        # GIVEN
        source = case
        expected = Token(keywords[expect], expect, 1, 1)
        lex = Lexer(StringIO(source), ErrorHandler())

        # WHEN
        token = lex.get_next_token()

        # THEN
        self.assertEqual(expected, token, "Keyword not detected correctly.")

    @parameterized.expand([
        ("\"test1\"", "test1"),
        ("'test2'", "test2"),
        ("\"\\\"test    3\"", "\"test    3"),
        ("\"\\'test_4\"", "'test_4"),
        ("'\\ntest5'", "\ntest5"),
        ("'\\n'", "\n"),
        ("'\\r'", "\r"),
        ("\"\\t\"", "\t"),
    ])
    def test_try_build_text_const(self, case, expect):
        # GIVEN
        source = case
        expected = Token(TokenType.T_TEXT_CONST, expect, 1, 1)
        lex = Lexer(StringIO(source), ErrorHandler())

        # WHEN
        token = lex.get_next_token()

        # THEN
        self.assertEqual(expected, token, "Text const not detected correctly.")

    @parameterized.expand([
        ("0", 0),
        ("1", 1),
        ("12", 12),
        ("5555555", 5555555),
        ("123 456", 123),
    ])
    def test_try_build_number(self, case, expect):
        # GIVEN
        source = case
        expected = Token(TokenType.T_NUMBER, expect, 1, 1)
        lex = Lexer(StringIO(source), ErrorHandler())

        # WHEN
        token = lex.get_next_token()

        # THEN
        self.assertEqual(expected, token, "Number not detected correctly.")

    @parameterized.expand([
        ("+", "+"), ("+=1234", "+="),
        ("-", "-"), ("-=  ", "-="),
        ("*", "*"), ("*=\n", "*="),
        ("/", "/"), ("/=aaaa", "/="), ("//", "//"),
        ("%", "%"), ("%=.", "%="),
        ("<", "<"), ("<=\3", "<="),
        (">", ">"), (">= ", ">="),
        ("=", "="), ("==", "=="), ("!=", "!="),
        ("(", "("), (")\n", ")"),
        ("[", "["), ("] 2", "]"),
        ("{", "{"), ("}2 ", "}"),
        (".", "."), (",a", ","),
        (";", ";"), (": \t\t\n", ":"),
    ])
    def test_try_build_operator(self, case, expect):
        # GIVEN
        source = case
        expected = Token(operators[expect], expect, 1, 1)
        lex = Lexer(StringIO(source), ErrorHandler())

        # WHEN
        token = lex.get_next_token()

        # THEN
        self.assertEqual(expected, token, "Operator not detected correctly.")


class TestLexerComplex(unittest.TestCase):
    @parameterized.expand([
        (
                "while true 12 asdf5",
                [
                    Token(TokenType.T_WHILE, "while", 1, 1),
                    Token(TokenType.T_TRUE, "true", 1, 7),
                    Token(TokenType.T_NUMBER, 12, 1, 12),
                    Token(TokenType.T_IDENTIFIER, "asdf5", 1, 15),
                    Token(TokenType.T_ETX, "\x03", 1, 20),
                ]
        ),
        (
                "   test = 5; 12 + 5 += 77 for i= 0 test2 \3",
                [
                    Token(TokenType.T_IDENTIFIER, "test", 1, 4),
                    Token(TokenType.T_ASSIGNMENT, "=", 1, 9),
                    Token(TokenType.T_NUMBER, 5, 1, 11),
                    Token(TokenType.T_SEMICOLON, ";", 1, 12),
                    Token(TokenType.T_NUMBER, 12, 1, 14),
                    Token(TokenType.T_PLUS, "+", 1, 17),
                    Token(TokenType.T_NUMBER, 5, 1, 19),
                    Token(TokenType.T_PLUS_ASSIGNMENT, "+=", 1, 21),
                    Token(TokenType.T_NUMBER, 77, 1, 24),
                    Token(TokenType.T_FOR, "for", 1, 27),
                    Token(TokenType.T_IDENTIFIER, "i", 1, 31),
                    Token(TokenType.T_ASSIGNMENT, "=", 1, 32),
                    Token(TokenType.T_NUMBER, 0, 1, 34),
                    Token(TokenType.T_IDENTIFIER, "test2", 1, 36),
                    Token(TokenType.T_ETX, "\x03", 1, 42),
                ]
        ),
    ])
    def test_get_next_token_one_line(self, source, expected):
        # GIVEN
        lex = Lexer(StringIO(source), ErrorHandler())
        result = []

        # WHEN
        token = lex.get_next_token()
        while token.type != TokenType.T_ETX:
            result.append(token)
            token = lex.get_next_token()
        result.append(token)  # T_ETX

        # THEN
        self.assertEqual(expected, result, "Wrong tokens detected.")

    @parameterized.expand([
        (
                "while(not test) {\n\tprint(12345);\n}\x03",
                [
                    Token(TokenType.T_WHILE, "while", 1, 1),
                    Token(TokenType.T_LEFT_BRACKET, "(", 1, 6),
                    Token(TokenType.T_NOT, "not", 1, 7),
                    Token(TokenType.T_IDENTIFIER, "test", 1, 11),
                    Token(TokenType.T_RIGHT_BRACKET, ")", 1, 15),
                    Token(TokenType.T_LEFT_CURLY_BRACKET, "{", 1, 17),
                    Token(TokenType.T_IDENTIFIER, "print", 2, 2),
                    Token(TokenType.T_LEFT_BRACKET, "(", 2, 7),
                    Token(TokenType.T_NUMBER, 12345, 2, 8),
                    Token(TokenType.T_RIGHT_BRACKET, ")", 2, 13),
                    Token(TokenType.T_SEMICOLON, ";", 2, 14),
                    Token(TokenType.T_RIGHT_CURLY_BRACKET, "}", 3, 1),
                    Token(TokenType.T_ETX, "\x03", 3, 2),
                ]
        ),
    ])
    def test_get_next_token_multiple_lines(self, source, expected):
        # GIVEN
        lex = Lexer(StringIO(source), ErrorHandler())
        result = []

        # WHEN
        token = lex.get_next_token()
        result.append(token)
        while token.type != TokenType.T_ETX:
            token = lex.get_next_token()
            result.append(token)

        # THEN
        self.assertEqual(expected, result, "Wrong tokens detected.")


class TestLexerErrorHandling(unittest.TestCase):
    @parameterized.expand([
        ('\1', '\1'),
        ("\2", "\2"),
    ])
    def test_detect_unknown_token(self, case, expect):
        # GIVEN
        source = case
        expected = Token(TokenType.T_UNKNOWN, expect, 1, 1)
        error_handler = ErrorHandler()
        error_handler.logger.setLevel(logging.CRITICAL)
        lex = Lexer(StringIO(source), error_handler)

        try:
            # WHEN
            lex.get_next_token()

            # THEN
            self.fail(f"Unknown token didn't throw an exception. ({case}, {expect})")
        except UnknownTokenLexerException as e:
            self.assertEqual(expected, e.token, "T_ILLEGAL not detected correctly.")

    @parameterized.expand([
        ('"\n', '\n'),
        ('\'\3', '\3'),
    ])
    def test_detect_text_const_break(self, case, expect):
        # GIVEN
        source = case
        expected = Token(TokenType.T_ILLEGAL, expect, 1, 2)
        error_handler = ErrorHandler()
        error_handler.logger.setLevel(logging.CRITICAL)
        lex = Lexer(StringIO(source), error_handler)

        try:
            # WHEN
            lex.get_next_token()

            # THEN
            self.fail(f"Unterminated text const didn't throw an exception. ({case}, {expect})")
        except UnterminatedStringLexerException as e:
            self.assertEqual(expected, e.token, "T_ILLEGAL not detected correctly.")

    @parameterized.expand([
        ("'" + "a" * (MAX_TEXT_CONST_LENGTH + 1) + "'",
         "a" * MAX_TEXT_CONST_LENGTH),
    ])
    def test_detect_text_const_too_long(self, case, expect):
        # GIVEN
        source = case
        expected = Token(TokenType.T_ILLEGAL, expect, 1, 1)
        error_handler = ErrorHandler()
        error_handler.logger.setLevel(logging.CRITICAL)
        lex = Lexer(StringIO(source), error_handler)

        try:
            # WHEN
            lex.get_next_token()

            # THEN
            self.fail("Too long text const didn't throw an exception.")
        except TextConstTooLongLexerException as e:
            self.assertEqual(expected, e.token, "T_ILLEGAL not detected correctly.")

    @parameterized.expand([
        ("b" * (MAX_IDENTIFIER_LENGTH + 1),
         "b" * MAX_IDENTIFIER_LENGTH),
    ])
    def test_detect_identifier_too_long(self, case, expect):
        # GIVEN
        source = case
        expected = Token(TokenType.T_ILLEGAL, expect, 1, 1)
        error_handler = ErrorHandler()
        error_handler.logger.setLevel(logging.CRITICAL)
        lex = Lexer(StringIO(source), error_handler)

        try:
            # WHEN
            lex.get_next_token()

            # THEN
            self.fail("Too long identifier didn't throw an exception.")
        except IdentifierTooLongLexerException as e:
            self.assertEqual(expected, e.token, "T_ILLEGAL not detected correctly.")

    @parameterized.expand([
        ("#" + "c" * (MAX_COMMENT_LENGTH + 1),
         "c" * MAX_COMMENT_LENGTH),
    ])
    def test_detect_comment_too_long(self, case, expect):
        # GIVEN
        source = case
        expected = Token(TokenType.T_ILLEGAL, expect, 1, 1)
        error_handler = ErrorHandler()
        error_handler.logger.setLevel(logging.CRITICAL)
        lex = Lexer(StringIO(source), error_handler)

        try:
            # WHEN
            lex.get_next_token()

            # THEN
            self.fail("Too long comment didn't throw an exception.")
        except CommentTooLongLexerException as e:
            self.assertEqual(expected, e.token, "T_ILLEGAL not detected correctly.")

    @parameterized.expand([
        ("2147483648",
         2147483648),
    ])
    def test_detect_integer_too_large(self, case, expect):
        # GIVEN
        source = case
        expected = Token(TokenType.T_ILLEGAL, expect, 1, 1)
        error_handler = ErrorHandler()
        error_handler.logger.setLevel(logging.CRITICAL)
        lex = Lexer(StringIO(source), error_handler)

        try:
            # WHEN
            lex.get_next_token()

            # THEN
            self.fail("Too large integer didn't throw an exception.")
        except IntegerTooLargeLexerException as e:
            self.assertEqual(expected, e.token, "T_ILLEGAL not detected correctly.")


if __name__ == '__main__':
    unittest.main()
