from Tutel.common.ErrorHandler import ErrorHandler
from Tutel.common.ErrorType import (
    MissingLeftBracketException,
    MissingRightBracketException,
    MissingIdentifierAfterCommaException,
    MissingRightCurlyBracketException,
    MissingSemicolonException,
    MissingRightSideOfAssignmentException,
    MissingConditionException,
    MissingBodyException,
    MissingIteratorException,
    MissingKeywordInException,
    MissingIterableException,
    ExprMissingRightSideException,
    MissingIdentifierAfterDotException,
    MissingRightSquareBracketException,
    MissingExpressionAfterCommaException,
    MissingFunctionBlockException,
    FunctionRedefinitionException, MissingEtx,
)
from Tutel.core.LexerModule.Lexer import Lexer
from Tutel.core.LexerModule.Tokens import TokenType, Token, TOKEN_VALUE_TYPES
from Tutel.core.ParserModule.Classes import (
    Program, Function, Block,
    Identifier,
    Statement,
    Assignment,
    Expression,
    ReturnStatement,
    IfStatement, ElifBlock, ElseBlock,
    ForStatement,
    WhileStatement,
    OrExpr, AndExpr, Negate,
    DotOperator, FunCall, ListElement, List, String, Integer, Boolean, Null, InvertExpr,
)
from Tutel.core.ParserModule.Remapper import assignment_mapper, comp_mapper, sum_mapper, mul_mapper


class LexerInterface:
    def __init__(self, lexer: Lexer) -> None:
        self.lexer = lexer
        self.lexer.get_next_token()
        while self.token.type == TokenType.T_COMMENT:
            self.lexer.get_next_token()

    def get_next_token(self) -> Token:
        self.lexer.get_next_token()
        while self.token.type == TokenType.T_COMMENT:
            self.lexer.get_next_token()
        return self.token

    def get_lineno(self) -> int:
        return self.lexer.token.line

    @property
    def token(self) -> Token:
        return self.lexer.token


class Parser:
    def __init__(self, error_handler: ErrorHandler = ErrorHandler(module="parser")) -> None:
        self.__lexer = None
        self.functions: dict[str, Function] = {}
        self.error_handler = error_handler

    @property
    def lexer(self) -> LexerInterface:
        return self.__lexer

    @lexer.setter
    def lexer(self, lexer: Lexer) -> None:
        self.__lexer = LexerInterface(lexer)

    def _check_and_consume(self, token_type: TokenType) -> bool:
        if not self._token_is(token_type):
            return False
        self.lexer.get_next_token()
        return True

    def _check_and_return(self, token_type: TokenType) -> TOKEN_VALUE_TYPES:
        if not self._token_is(token_type):
            return None
        value = self.lexer.token.value
        self.lexer.get_next_token()
        return value

    def _token_is(self, token_type: TokenType) -> bool:
        return self.lexer.token.type == token_type

    def parse(self, lexer: Lexer) -> Program:
        self.lexer = lexer
        self.functions = {}
        lineno = self.lexer.get_lineno()

        while self.try_parse_function_def():
            pass

        if not self._token_is(TokenType.T_ETX):
            self.error_handler.handle_error(
                MissingEtx(self.parse.__name__, self.lexer.token))

        return Program(functions=self.functions, lineno=lineno)

    def try_parse_function_def(self) -> bool:
        lineno = self.lexer.get_lineno()
        if not self._token_is(TokenType.T_IDENTIFIER):
            return False

        if self.lexer.token.value in self.functions:
            self.error_handler.handle_error(
                FunctionRedefinitionException(self.try_parse_function_def.__name__, self.lexer.token))

        function_name = self._check_and_return(TokenType.T_IDENTIFIER)

        if not self._check_and_consume(TokenType.T_LEFT_BRACKET):
            self.error_handler.handle_error(
                MissingLeftBracketException(self.try_parse_function_def.__name__, self.lexer.token))

        params = self.try_parse_params_list()

        if not self._check_and_consume(TokenType.T_RIGHT_BRACKET):
            self.error_handler.handle_error(
                MissingRightBracketException(self.try_parse_function_def.__name__, self.lexer.token))

        if (block := self.try_parse_block()) is None:
            self.error_handler.handle_error(
                MissingFunctionBlockException(self.try_parse_function_def.__name__, self.lexer.token))

        self.functions[function_name] = Function(Identifier(function_name, lineno), params, block, lineno)

        return True

    def try_parse_params_list(self) -> list[Identifier]:
        params: list[Identifier] = []
        parameter: Identifier
        if not (parameter := self.try_parse_identifier()):
            return params
        params.append(parameter)

        while self._check_and_consume(TokenType.T_COMMA):
            if not (parameter := self.try_parse_identifier()):
                self.error_handler.handle_error(
                    MissingIdentifierAfterCommaException(self.try_parse_params_list.__name__, self.lexer.token))

            params.append(parameter)

        return params

    def try_parse_block(self) -> Block | None:
        lineno = self.lexer.get_lineno()
        statements: list[Statement] = []
        instruction: Statement

        if not self._check_and_consume(TokenType.T_LEFT_CURLY_BRACKET):
            return None

        while instruction := self.try_parse_statement():
            statements.append(instruction)

        if not self._check_and_consume(TokenType.T_RIGHT_CURLY_BRACKET):
            self.error_handler.handle_error(
                MissingRightCurlyBracketException(self.try_parse_block.__name__, self.lexer.token))

        return Block(statements, lineno)

    def try_parse_statement(self) -> Statement | None:
        if statement := self.try_parse_simple_statement():
            if not self._check_and_consume(TokenType.T_SEMICOLON):
                self.error_handler.handle_error(
                    MissingSemicolonException(self.try_parse_statement.__name__, self.lexer.token))
            return statement

        if statement := self.try_parse_compound_statement():
            return statement

        return None

    def try_parse_simple_statement(self) -> Statement | None:
        if expression := self.try_parse_expression():
            if assignment := self.try_parse_assignment(expression):
                return assignment
            return expression

        if statement := self.try_parse_return_statement():
            return statement

        return None

    def try_parse_compound_statement(self) -> Statement | None:
        if statement := self.try_parse_if_statement():
            return statement

        if statement := self.try_parse_for_statement():
            return statement

        if statement := self.try_parse_while_statement():
            return statement

        return None

    def try_parse_assignment(self, left_side: Expression) -> Assignment | None:
        lineno = self.lexer.get_lineno()
        if not (assignment_type := assignment_mapper.get(self.lexer.token.type)):
            return None

        self.lexer.get_next_token()

        if not (right_side := self.try_parse_expression()):
            self.error_handler.handle_error(
                MissingRightSideOfAssignmentException(self.try_parse_assignment.__name__, self.lexer.token))

        return assignment_type(left_side, right_side, lineno)

    def try_parse_return_statement(self) -> ReturnStatement | None:
        lineno = self.lexer.get_lineno()
        if not self._check_and_consume(TokenType.T_RETURN):
            return None

        return_values = self.try_parse_return_values()

        return ReturnStatement(return_values, lineno)

    def try_parse_return_values(self) -> list[Expression]:
        expressions: list[Expression] = []
        expression: Expression

        if not (expression := self.try_parse_expression()):
            return expressions
        expressions.append(expression)

        while self._check_and_consume(TokenType.T_COMMA):
            if not (expression := self.try_parse_expression()):
                self.error_handler.handle_error(
                    MissingExpressionAfterCommaException(self.try_parse_params_list.__name__, self.lexer.token))

            expressions.append(expression)

        return expressions

    def try_parse_if_statement(self) -> IfStatement | None:
        lineno = self.lexer.get_lineno()
        condition: Expression
        body: Block

        if not self._check_and_consume(TokenType.T_IF):
            return None

        if not self._check_and_consume(TokenType.T_LEFT_BRACKET):
            self.error_handler.handle_error(
                MissingLeftBracketException(self.try_parse_if_statement.__name__, self.lexer.token))

        if not (condition := self.try_parse_expression()):
            self.error_handler.handle_error(
                MissingConditionException(self.try_parse_if_statement.__name__, self.lexer.token))

        if not self._check_and_consume(TokenType.T_RIGHT_BRACKET):
            self.error_handler.handle_error(
                MissingRightBracketException(self.try_parse_if_statement.__name__, self.lexer.token))

        if (body := self.try_parse_compound_statement_body()) is None:
            self.error_handler.handle_error(
                MissingBodyException(self.try_parse_if_statement.__name__, self.lexer.token))

        elif_blocks: list[ElifBlock] = []

        while elif_block := self.try_parse_elif_block():
            elif_blocks.append(elif_block)

        else_block = self.try_parse_else_block()

        return IfStatement(condition, body, elif_blocks, else_block, lineno)

    def try_parse_elif_block(self) -> ElifBlock | None:
        lineno = self.lexer.get_lineno()
        condition: Expression
        body: Block

        if not self._check_and_consume(TokenType.T_ELIF):
            return None

        if not self._check_and_consume(TokenType.T_LEFT_BRACKET):
            self.error_handler.handle_error(
                MissingLeftBracketException(self.try_parse_elif_block.__name__, self.lexer.token))

        if not (condition := self.try_parse_expression()):
            self.error_handler.handle_error(
                MissingConditionException(self.try_parse_elif_block.__name__, self.lexer.token))

        if not self._check_and_consume(TokenType.T_RIGHT_BRACKET):
            self.error_handler.handle_error(
                MissingRightBracketException(self.try_parse_elif_block.__name__, self.lexer.token))

        if (body := self.try_parse_compound_statement_body()) is None:
            self.error_handler.handle_error(MissingBodyException(self.try_parse_elif_block.__name__, self.lexer.token))

        return ElifBlock(condition, body, lineno)

    def try_parse_else_block(self) -> ElseBlock | None:
        lineno = self.lexer.get_lineno()
        body: Block

        if not self._check_and_consume(TokenType.T_ELSE):
            return None

        if (body := self.try_parse_compound_statement_body()) is None:
            self.error_handler.handle_error(MissingBodyException(self.try_parse_else_block.__name__, self.lexer.token))

        return ElseBlock(body, lineno)

    def try_parse_for_statement(self) -> ForStatement | None:
        lineno = self.lexer.get_lineno()
        iterator: Identifier
        iterable: Expression
        body: Block

        if not self._check_and_consume(TokenType.T_FOR):
            return None

        if not self._check_and_consume(TokenType.T_LEFT_BRACKET):
            self.error_handler.handle_error(
                MissingLeftBracketException(self.try_parse_for_statement.__name__, self.lexer.token))

        if not (iterator := self.try_parse_identifier()):
            self.error_handler.handle_error(
                MissingIteratorException(self.try_parse_for_statement.__name__, self.lexer.token))

        if not self._check_and_consume(TokenType.T_IN):
            self.error_handler.handle_error(
                MissingKeywordInException(self.try_parse_for_statement.__name__, self.lexer.token))

        if not (iterable := self.try_parse_expression()):
            self.error_handler.handle_error(
                MissingIterableException(self.try_parse_for_statement.__name__, self.lexer.token))

        if not self._check_and_consume(TokenType.T_RIGHT_BRACKET):
            self.error_handler.handle_error(
                MissingRightBracketException(self.try_parse_for_statement.__name__, self.lexer.token))

        if (body := self.try_parse_compound_statement_body()) is None:
            self.error_handler.handle_error(
                MissingBodyException(self.try_parse_for_statement.__name__, self.lexer.token))

        return ForStatement(iterator, iterable, body, lineno)

    def try_parse_while_statement(self) -> WhileStatement | None:
        lineno = self.lexer.get_lineno()
        condition: Expression
        body: Block

        if not self._check_and_consume(TokenType.T_WHILE):
            return None

        if not self._check_and_consume(TokenType.T_LEFT_BRACKET):
            self.error_handler.handle_error(
                MissingLeftBracketException(self.try_parse_while_statement.__name__, self.lexer.token))

        if not (condition := self.try_parse_expression()):
            self.error_handler.handle_error(
                MissingConditionException(self.try_parse_while_statement.__name__, self.lexer.token))

        if not self._check_and_consume(TokenType.T_RIGHT_BRACKET):
            self.error_handler.handle_error(
                MissingRightBracketException(self.try_parse_while_statement.__name__, self.lexer.token))

        if not (body := self.try_parse_compound_statement_body()):
            self.error_handler.handle_error(
                MissingBodyException(self.try_parse_while_statement.__name__, self.lexer.token))

        return WhileStatement(condition, body, lineno)

    def try_parse_compound_statement_body(self) -> Block | None:
        lineno = self.lexer.get_lineno()
        block: Block
        statement: Statement

        if (block := self.try_parse_block()) is not None:
            return block

        if statement := self.try_parse_statement():
            return Block([statement], lineno)

        return None

    def try_parse_expression(self) -> Expression | None:
        lineno = self.lexer.get_lineno()
        if not (left_expr := self.try_parse_or_expr()):
            return None

        while self._check_and_consume(TokenType.T_OR):
            if not (right_expr := self.try_parse_or_expr()):
                self.error_handler.handle_error(
                    ExprMissingRightSideException(self.try_parse_expression.__name__, self.lexer.token))

            left_expr = OrExpr(left_expr, right_expr, lineno)

        return left_expr

    def try_parse_or_expr(self) -> Expression | None:
        lineno = self.lexer.get_lineno()
        if not (left_expr := self.try_parse_and_expr()):
            return None

        while self._check_and_consume(TokenType.T_AND):
            if not (right_expr := self.try_parse_and_expr()):
                self.error_handler.handle_error(
                    ExprMissingRightSideException(self.try_parse_or_expr.__name__, self.lexer.token))

            left_expr = AndExpr(left_expr, right_expr, lineno)

        return left_expr

    def try_parse_and_expr(self) -> Expression | None:
        lineno = self.lexer.get_lineno()
        negate = False
        at_least_one = False
        while self._check_and_consume(TokenType.T_NOT):
            negate = not negate
            at_least_one = True

        if not (expr := self.try_parse_negate_expr()):
            if at_least_one:
                self.error_handler.handle_error(
                    ExprMissingRightSideException(self.try_parse_and_expr.__name__, self.lexer.token))
            return None

        if negate:
            return Negate(expr, lineno)

        return expr

    def try_parse_negate_expr(self) -> Expression | None:
        lineno = self.lexer.get_lineno()
        if not (left_expr := self.try_parse_comp_expr()):
            return None

        if comp_type := comp_mapper.get(self.lexer.token.type):
            self.lexer.get_next_token()
            if not (right_expr := self.try_parse_comp_expr()):
                self.error_handler.handle_error(
                    ExprMissingRightSideException(self.try_parse_negate_expr.__name__, self.lexer.token))

            left_expr = comp_type(left_expr, right_expr, lineno)

        return left_expr

    def try_parse_comp_expr(self) -> Expression | None:
        lineno = self.lexer.get_lineno()
        if not (left_expr := self.try_parse_sum_expr()):
            return None

        while sum_type := sum_mapper.get(self.lexer.token.type):
            self.lexer.get_next_token()
            if not (right_expr := self.try_parse_sum_expr()):
                self.error_handler.handle_error(
                    ExprMissingRightSideException(self.try_parse_comp_expr.__name__, self.lexer.token))

            left_expr = sum_type(left_expr, right_expr, lineno)

        return left_expr

    def try_parse_sum_expr(self) -> Expression | None:
        lineno = self.lexer.get_lineno()
        if not (left_expr := self.try_parse_mul_expr()):
            return None

        while mul_type := mul_mapper.get(self.lexer.token.type):
            self.lexer.get_next_token()
            if not (right_expr := self.try_parse_mul_expr()):
                self.error_handler.handle_error(
                    ExprMissingRightSideException(self.try_parse_sum_expr.__name__, self.lexer.token))

            left_expr = mul_type(left_expr, right_expr, lineno)

        return left_expr

    def try_parse_mul_expr(self) -> Expression | None:
        negate = False
        at_least_one = False
        while self._token_is(TokenType.T_MINUS) \
                or self._token_is(TokenType.T_PLUS):
            if self._token_is(TokenType.T_MINUS):
                negate = not negate
            self.lexer.get_next_token()
            at_least_one = True

        if not (expr := self.try_parse_atom_complex()):
            if at_least_one:
                self.error_handler.handle_error(
                    ExprMissingRightSideException(self.try_parse_mul_expr.__name__, self.lexer.token))
            return None

        if negate:
            return InvertExpr(expr)

        return expr

    def try_parse_atom_complex(self) -> Expression | None:
        if expr := self.try_parse_atom():
            while new_expr := self.try_parse_complex(expr):
                expr = new_expr

            return expr

    def try_parse_atom(self) -> Expression | None:
        lineno = self.lexer.get_lineno()

        if (expr := self.try_parse_identifier()) is not None:
            return expr

        if (expr := self.try_parse_parenthesis()) is not None:
            return expr

        if (expr := self.try_parse_list()) is not None:
            return expr

        if (string := self._check_and_return(TokenType.T_TEXT_CONST)) is not None:
            return String(string, lineno)

        if (number := self._check_and_return(TokenType.T_NUMBER)) is not None:
            return Integer(number, lineno)

        if self._token_is(TokenType.T_TRUE):
            self.lexer.get_next_token()
            return Boolean(True, lineno)

        if self._token_is(TokenType.T_FALSE):
            self.lexer.get_next_token()
            return Boolean(False, lineno)

        if self._token_is(TokenType.T_NULL):
            self.lexer.get_next_token()
            return Null(lineno)

        return None

    def try_parse_complex(self, left_expr: Expression) -> Expression | None:
        if right_expr := self.try_parse_dot_operator(left_expr):
            return right_expr

        if right_expr := self.try_parse_fun_call(left_expr):
            return right_expr

        if right_expr := self.try_parse_list_element(left_expr):
            return right_expr

        return None

    def try_parse_dot_operator(self, left_expr: Expression) -> Expression | None:
        lineno = self.lexer.get_lineno()
        if not self._check_and_consume(TokenType.T_DOT):
            return None

        if not (identifier := self.try_parse_identifier()):
            self.error_handler.handle_error(
                MissingIdentifierAfterDotException(self.try_parse_dot_operator.__name__, self.lexer.token))

        return DotOperator(left_expr, identifier, lineno)

    def try_parse_fun_call(self, left_expr: Expression) -> Expression | None:
        lineno = self.lexer.get_lineno()
        if not self._check_and_consume(TokenType.T_LEFT_BRACKET):
            return None

        arguments = self.try_parse_arguments()

        if not self._check_and_consume(TokenType.T_RIGHT_BRACKET):
            self.error_handler.handle_error(
                MissingRightBracketException(self.try_parse_fun_call.__name__, self.lexer.token))

        return FunCall(left_expr, arguments, lineno)

    def try_parse_arguments(self) -> list[Expression]:
        arguments: list[Expression] = []
        argument: Expression
        if not (argument := self.try_parse_expression()):
            return arguments
        arguments.append(argument)

        while self._check_and_consume(TokenType.T_COMMA):
            if not (argument := self.try_parse_expression()):
                self.error_handler.handle_error(
                    MissingExpressionAfterCommaException(self.try_parse_params_list.__name__, self.lexer.token))

            arguments.append(argument)

        return arguments

    def try_parse_list_element(self, left_expr: Expression) -> Expression | None:
        lineno = self.lexer.get_lineno()
        if not self._check_and_consume(TokenType.T_LEFT_SQUARE_BRACKET):
            return None

        right_expr = self.try_parse_expression()

        if not self._check_and_consume(TokenType.T_RIGHT_SQUARE_BRACKET):
            self.error_handler.handle_error(
                MissingRightSquareBracketException(self.try_parse_list_element.__name__, self.lexer.token))

        return ListElement(left_expr, right_expr, lineno)

    def try_parse_parenthesis(self) -> Expression | None:
        if not self._check_and_consume(TokenType.T_LEFT_BRACKET):
            return None

        expr = self.try_parse_expression()

        if not self._check_and_consume(TokenType.T_RIGHT_BRACKET):
            self.error_handler.handle_error(
                MissingRightBracketException(self.try_parse_parenthesis.__name__, self.lexer.token))

        return expr

    def try_parse_list(self) -> Expression | None:
        lineno = self.lexer.get_lineno()
        if not self._check_and_consume(TokenType.T_LEFT_SQUARE_BRACKET):
            return None

        elements: list[Expression] = []

        if not (element := self.try_parse_expression()):
            if not self._check_and_consume(TokenType.T_RIGHT_SQUARE_BRACKET):
                self.error_handler.handle_error(
                    MissingRightSquareBracketException(self.try_parse_list.__name__, self.lexer.token))
            return List(elements, lineno)
        elements.append(element)

        while self._check_and_consume(TokenType.T_COMMA):
            if not (element := self.try_parse_expression()):
                self.error_handler.handle_error(
                    MissingExpressionAfterCommaException(self.try_parse_list.__name__, self.lexer.token))

            elements.append(element)

        if not self._check_and_consume(TokenType.T_RIGHT_SQUARE_BRACKET):
            self.error_handler.handle_error(
                MissingRightSquareBracketException(self.try_parse_list.__name__, self.lexer.token))

        return List(elements, lineno)

    def try_parse_identifier(self) -> Identifier | None:
        lineno = self.lexer.get_lineno()
        if not (identifier := self._check_and_return(TokenType.T_IDENTIFIER)):
            return None

        return Identifier(identifier, lineno)
