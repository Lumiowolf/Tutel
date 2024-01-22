import logging
import unittest
from io import StringIO

from parameterized import parameterized

from Tutel.common.ErrorHandler import ErrorHandler
from Tutel.common.ErrorType import IdentifierTooLongLexerException, TextConstTooLongLexerException, \
    CommentTooLongLexerException, \
    UnknownTokenLexerException, UnterminatedStringLexerException, IntegerTooLargeLexerException, \
    LeadingZerosInIntegerLexerException, UnknownEscapingLexerException
from Tutel.core.LexerModule.Lexer import Lexer, Token
from Tutel.core.LexerModule.Lexer import MAX_IDENTIFIER_LENGTH, MAX_TEXT_CONST_LENGTH, MAX_COMMENT_LENGTH
from Tutel.core.LexerModule.Lexer import operators, TokenType, keywords


class TestLexerSimple(unittest.TestCase):
    @parameterized.expand([
        ("\ntest", Token(TokenType.T_IDENTIFIER, "test", 2, 1)),
        ("\n\rtest", Token(TokenType.T_IDENTIFIER, "test", 2, 1)),
        ("\rtest", Token(TokenType.T_IDENTIFIER, "test", 2, 1)),
        ("\r\ntest", Token(TokenType.T_IDENTIFIER, "test", 2, 1)),
        (" test", Token(TokenType.T_IDENTIFIER, "test", 1, 2)),
        ("\n test", Token(TokenType.T_IDENTIFIER, "test", 2, 2)),
    ])
    def test_skip_whites(self, case, expect):
        # GIVEN
        source = case
        lexer = Lexer(StringIO(source), get_error_handler())

        # WHEN
        token = lexer.get_next_token()

        # THEN
        self.assertEqual(expect, token, "Whites not skipped correctly.")

    def test_try_build_etx(self):
        # GIVEN
        source = "\x03"
        expected = Token(TokenType.T_ETX, '\x03', 1, 1)
        lexer = Lexer(StringIO(source), get_error_handler())

        # WHEN
        token = lexer.get_next_token()

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
        lexer = Lexer(StringIO(source), get_error_handler())

        # WHEN
        token = lexer.get_next_token()

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
        lexer = Lexer(StringIO(source), get_error_handler())

        # WHEN
        token = lexer.get_next_token()

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
        lexer = Lexer(StringIO(source), get_error_handler())

        # WHEN
        token = lexer.get_next_token()

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
        lexer = Lexer(StringIO(source), get_error_handler())

        # WHEN
        token = lexer.get_next_token()

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
        lexer = Lexer(StringIO(source), get_error_handler())

        # WHEN
        token = lexer.get_next_token()

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
        (";", ";"),
    ])
    def test_try_build_operator(self, case, expect):
        # GIVEN
        source = case
        expected = Token(operators[expect], expect, 1, 1)
        lexer = Lexer(StringIO(source), get_error_handler())

        # WHEN
        token = lexer.get_next_token()

        # THEN
        self.assertEqual(expected, token, "Operator not detected correctly.")


class TestLexerComplexer(unittest.TestCase):
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
        lexer = Lexer(StringIO(source), get_error_handler())
        result = []

        # WHEN
        token = lexer.get_next_token()
        while token.type != TokenType.T_ETX:
            result.append(token)
            token = lexer.get_next_token()
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
        lexer = Lexer(StringIO(source), get_error_handler())
        result = []

        # WHEN
        token = lexer.get_next_token()
        result.append(token)
        while token.type != TokenType.T_ETX:
            token = lexer.get_next_token()
            result.append(token)

        # THEN
        self.assertEqual(expected, result, "Wrong tokens detected.")


def get_error_handler():
    return ErrorHandler(module="test_lexer", level=logging.CRITICAL)


class TestLexerErrorHandling(unittest.TestCase):
    @parameterized.expand([
        ('\1', '\1'),
        ("\2", "\2"),
    ])
    def test_detect_unknown_token(self, case, expect):
        # GIVEN
        source = case
        expected = Token(TokenType.T_UNKNOWN, expect, 1, 1)
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(source), error_handler)

        # THEN
        self.assertRaises(UnknownTokenLexerException, lexer.get_next_token)
        self.assertEqual(expected, lexer.token, "T_ILLEGAL not detected correctly.")

    @parameterized.expand([
        ('"\n', '\n'),
        ('\'\3', '\3'),
    ])
    def test_detect_text_const_break(self, case, expect):
        # GIVEN
        source = case
        expected = Token(TokenType.T_ILLEGAL, expect, 1, 2)
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(source), error_handler)

        # THEN
        self.assertRaises(UnterminatedStringLexerException, lexer.get_next_token)
        self.assertEqual(expected, lexer.token, "T_ILLEGAL not detected correctly.")

    @parameterized.expand([
        ("'" + "a" * (MAX_TEXT_CONST_LENGTH + 1) + "'",
         "a" * MAX_TEXT_CONST_LENGTH),
    ])
    def test_detect_text_const_too_long(self, case, expect):
        # GIVEN
        source = case
        expected = Token(TokenType.T_ILLEGAL, expect, 1, 1)
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(source), error_handler)

        # THEN
        self.assertRaises(TextConstTooLongLexerException, lexer.get_next_token)
        self.assertEqual(expected, lexer.token, "T_ILLEGAL not detected correctly.")

    @parameterized.expand([
        ("b" * (MAX_IDENTIFIER_LENGTH + 1),
         "b" * MAX_IDENTIFIER_LENGTH),
    ])
    def test_detect_identifier_too_long(self, case, expect):
        # GIVEN
        source = case
        expected = Token(TokenType.T_ILLEGAL, expect, 1, 1)
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(source), error_handler)

        # THEN
        self.assertRaises(IdentifierTooLongLexerException, lexer.get_next_token)
        self.assertEqual(expected, lexer.token, "T_ILLEGAL not detected correctly.")

    @parameterized.expand([
        ("#" + "c" * (MAX_COMMENT_LENGTH + 1),
         "c" * MAX_COMMENT_LENGTH),
    ])
    def test_detect_comment_too_long(self, case, expect):
        # GIVEN
        source = case
        expected = Token(TokenType.T_ILLEGAL, expect, 1, 1)
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(source), error_handler)

        # THEN
        self.assertRaises(CommentTooLongLexerException, lexer.get_next_token)
        self.assertEqual(expected, lexer.token, "T_ILLEGAL not detected correctly.")

    @parameterized.expand([
        ("2147483648",
         2147483648),
    ])
    def test_detect_integer_too_large(self, case, expect):
        # GIVEN
        source = case
        expected = Token(TokenType.T_ILLEGAL, expect, 1, 1)
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(source), error_handler)

        # THEN
        self.assertRaises(IntegerTooLargeLexerException, lexer.get_next_token)
        self.assertEqual(expected, lexer.token, "T_ILLEGAL not detected correctly.")

    @parameterized.expand([
        ("01",
         "1"),
    ])
    def test_detect_leading_zeros_in_integer(self, case, expect):
        # GIVEN
        source = case
        expected = Token(TokenType.T_ILLEGAL, expect, 1, 2)
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(source), error_handler)

        # THEN
        self.assertRaises(LeadingZerosInIntegerLexerException, lexer.get_next_token)
        self.assertEqual(expected, lexer.token, "T_ILLEGAL not detected correctly.")

    @parameterized.expand([
        ("'\\a'",
         "\\a"),
    ])
    def test_detect_unknown_escaping(self, case, expect):
        # GIVEN
        source = case
        expected = Token(TokenType.T_ILLEGAL, expect, 1, 2)
        error_handler = get_error_handler()
        lexer = Lexer(StringIO(source), error_handler)

        # THEN
        self.assertRaises(UnknownEscapingLexerException, lexer.get_next_token)
        self.assertEqual(expected, lexer.token, "T_ILLEGAL not detected correctly.")


def suite():
    suite_ = unittest.TestSuite()
    suite_.addTest(unittest.makeSuite(TestLexerSimple, 'test'))
    suite_.addTest(unittest.makeSuite(TestLexerComplexer, 'test'))
    suite_.addTest(unittest.makeSuite(TestLexerErrorHandling, 'test'))
    return suite_
