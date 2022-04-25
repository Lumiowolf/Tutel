import logging
import unittest
from io import StringIO

from parameterized import parameterized

from LexerModule.lexer import Lexer, Token, TokenType, keywords
from LexerModule.tokens import operators, punctuations


class TestLexerSimple(unittest.TestCase):
    def test_try_build_etx(self):
        # GIVEN
        source = "\x03"
        expected = Token(TokenType.T_ETX, '\x03', 0, 0)
        lex = Lexer(StringIO(source))

        # WHEN
        lex._try_build_etx()

        # THEN
        self.assertEqual(expected, lex.token, "ETX not detected correctly.")

    @parameterized.expand([
        ("# test1", " test1"),
        ("#    test 2", "    test 2"),
        ("#test 3\n test3", "test 3"),
    ])
    def test_try_build_comment(self, case, expect):
        # GIVEN
        source = case
        expected = Token(TokenType.T_COMMENT, expect, 0, 0)
        lex = Lexer(StringIO(source))

        # WHEN
        lex._try_build_comment()

        # THEN
        self.assertEqual(expected, lex.token, "Comment not detected correctly.")

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
        expected = Token(TokenType.T_IDENTIFIER, expect, 0, 0)
        lex = Lexer(StringIO(source))

        # WHEN
        lex._try_build_identifier_or_keyword()

        # THEN
        self.assertEqual(expected, lex.token, "Identifier not detected correctly.")

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
        expected = Token(keywords[expect], expect, 0, 0)
        lex = Lexer(StringIO(source))

        # WHEN
        lex._try_build_identifier_or_keyword()

        # THEN
        self.assertEqual(expected, lex.token, "Keyword not detected correctly.")

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
        expected = Token(TokenType.T_TEXT_CONST, expect, 0, 0)
        lex = Lexer(StringIO(source))

        # WHEN
        lex._try_build_text_const()

        # THEN
        self.assertEqual(expected, lex.token, "Text const not detected correctly.")

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
        expected = Token(TokenType.T_NUMBER, expect, 0, 0)
        lex = Lexer(StringIO(source))

        # WHEN
        lex._try_build_number()

        # THEN
        self.assertEqual(expected, lex.token, "Number not detected correctly.")

    @parameterized.expand([
        ("+", "+"), ("+=1234", "+="),
        ("-", "-"), ("-=  ", "-="),
        ("*", "*"), ("*=\n", "*="),
        ("/", "/"), ("/=aaaa", "/="), ("//", "//"),
        ("%", "%"), ("%=.", "%="),
        ("<", "<"), ("<=\3", "<="),
        (">", ">"), (">= ", ">="),
        ("=", "="), ("==", "=="), ("!=", "!="),
    ])
    def test_try_build_operator(self, case, expect):
        # GIVEN
        source = case
        expected = Token(operators[expect], expect, 0, 0)
        lex = Lexer(StringIO(source))

        # WHEN
        lex._try_build_operator()

        # THEN
        self.assertEqual(expected, lex.token, "Operator not detected correctly.")

    @parameterized.expand([
        ("'", "'"), ("\"", "\""),
        ("(", "("), (")\n", ")"),
        ("[", "["), ("] 2", "]"),
        ("{", "{"), ("}2 ", "}"),
        (".", "."), (",a", ","),
        (";", ";"), (": \t\t\n", ":")
    ])
    def test_try_build_punctuation(self, case, expect):
        # GIVEN
        source = case
        expected = Token(punctuations[expect], expect, 0, 0)
        lex = Lexer(StringIO(source))

        # WHEN
        lex._try_build_punctuation()

        # THEN
        self.assertEqual(expected, lex.token, "Punctuation mark not detected correctly.")


class TestLexerComplex(unittest.TestCase):
    @parameterized.expand([
        (
                "while true 12 asdf5",
                [
                    Token(TokenType.T_WHILE, "while", 0, 0),
                    Token(TokenType.T_TRUE, "true", 0, 6),
                    Token(TokenType.T_NUMBER, 12, 0, 11),
                    Token(TokenType.T_IDENTIFIER, "asdf5", 0, 14),
                    Token(TokenType.T_ETX, "\x03", 0, 19),
                ]
        ),
        (
                "   test = 5; 12 + 5 += 77 for i= 0 test2 \3",
                [
                    Token(TokenType.T_IDENTIFIER, "test", 0, 3),
                    Token(TokenType.T_ASSIGNMENT, "=", 0, 8),
                    Token(TokenType.T_NUMBER, 5, 0, 10),
                    Token(TokenType.T_SEMICOLON, ";", 0, 11),
                    Token(TokenType.T_NUMBER, 12, 0, 13),
                    Token(TokenType.T_PLUS, "+", 0, 16),
                    Token(TokenType.T_NUMBER, 5, 0, 18),
                    Token(TokenType.T_PLUS_ASSIGNMENT, "+=", 0, 20),
                    Token(TokenType.T_NUMBER, 77, 0, 23),
                    Token(TokenType.T_FOR, "for", 0, 26),
                    Token(TokenType.T_IDENTIFIER, "i", 0, 30),
                    Token(TokenType.T_ASSIGNMENT, "=", 0, 31),
                    Token(TokenType.T_NUMBER, 0, 0, 33),
                    Token(TokenType.T_IDENTIFIER, "test2", 0, 35),
                    Token(TokenType.T_ETX, "\x03", 0, 41),
                ]
        ),
    ])
    def test_get_next_token_one_line(self, source, expected):
        # GIVEN
        lex = Lexer(StringIO(source))
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
                    Token(TokenType.T_WHILE, "while", 0, 0),
                    Token(TokenType.T_LEFT_BRACKET, "(", 0, 5),
                    Token(TokenType.T_NOT, "not", 0, 6),
                    Token(TokenType.T_IDENTIFIER, "test", 0, 10),
                    Token(TokenType.T_RIGHT_BRACKET, ")", 0, 14),
                    Token(TokenType.T_LEFT_CURLY_BRACKET, "{", 0, 16),
                    Token(TokenType.T_IDENTIFIER, "print", 1, 1),
                    Token(TokenType.T_LEFT_BRACKET, "(", 1, 6),
                    Token(TokenType.T_NUMBER, 12345, 1, 7),
                    Token(TokenType.T_RIGHT_BRACKET, ")", 1, 12),
                    Token(TokenType.T_SEMICOLON, ";", 1, 13),
                    Token(TokenType.T_RIGHT_CURLY_BRACKET, "}", 2, 0),
                    Token(TokenType.T_ETX, "\x03", 2, 1),
                ]
        ),
    ])
    def test_get_next_token_multiple_lines(self, source, expected):
        # GIVEN
        lex = Lexer(StringIO(source))
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
        ("==!", "==!"),
        ("++", "++"),
        ("!==", "!=="),
        ("%%", "%%"),
    ])
    def test_detect_unknown_token(self, case, expect):
        # GIVEN
        source = case
        expected = Token(TokenType.T_UNKNOWN, expect, 0, 0)
        lex = Lexer(StringIO(source))
        # Silence error logs
        # lex._error_handler.logger.setLevel(logging.CRITICAL)

        # WHEN
        lex.get_next_token()

        # THEN
        self.assertEqual(expected, lex.token, "T_UNKNOWN not detected correctly.")

    @parameterized.expand([
        ('"\n', '\n'),
        ('\'\3', '\3'),
    ])
    def test_detect_string_const_break(self, case, expect):
        # GIVEN
        source = case
        expected = Token(TokenType.T_ILLEGAL, expect, 0, 1)
        lex = Lexer(StringIO(source))
        # Silence error logs
        # lex._error_handler.logger.setLevel(logging.CRITICAL)

        # WHEN
        lex.get_next_token()

        # THEN
        self.assertEqual(expected, lex.token, "T_ILLEGAL not detected correctly.")

    @parameterized.expand([
        ('asdfghjkasdfghjkasdfghjkasdfghjkasdfghjkasdfghjkasdfghjkasdfghjka',
         'asdfghjkasdfghjkasdfghjkasdfghjkasdfghjkasdfghjkasdfghjkasdfghjka...'),
    ])
    def test_detect_identifier_too_long(self, case, expect):
        # GIVEN
        source = case
        expected = Token(TokenType.T_ILLEGAL, expect, 0, 0)
        lex = Lexer(StringIO(source))
        # Silence error logs
        # lex._error_handler.logger.setLevel(logging.CRITICAL)

        # WHEN
        lex.get_next_token()

        # THEN
        self.assertEqual(expected, lex.token, "T_ILLEGAL not detected correctly.")


if __name__ == '__main__':
    unittest.main()
