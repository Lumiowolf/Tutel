from Tutel.LexerModule.Tokens import TokenType
from Tutel.ParserModule.Classes import EqExpr, NotEqExpr, LessExpr, GreaterExpr, LessEqExpr, GreaterEqExpr, InExpr, \
    AddExpr, \
    SubExpr, BasicAssignment, AddAssignment, SubAssignment, MulAssignment, DivAssignment, ModAssignment, MulExpr, \
    DivExpr, ModExpr, IntDivExpr

mul_mapper: dict[TokenType, type] = {
    TokenType.T_MULTIPLY: MulExpr,
    TokenType.T_DIVIDE: DivExpr,
    TokenType.T_MODULUS: ModExpr,
    TokenType.T_INT_DIVIDE: IntDivExpr,
}

assignment_mapper: dict[TokenType, type] = {
    TokenType.T_ASSIGNMENT: BasicAssignment,
    TokenType.T_PLUS_ASSIGNMENT: AddAssignment,
    TokenType.T_MINUS_ASSIGNMENT: SubAssignment,
    TokenType.T_MULTIPLY_ASSIGNMENT: MulAssignment,
    TokenType.T_DIVIDE_ASSIGNMENT: DivAssignment,
    TokenType.T_MODULUS_ASSIGNMENT: ModAssignment,
}

comp_mapper: dict[TokenType, type] = {
    TokenType.T_EQUAL: EqExpr,
    TokenType.T_NOTEQUAL: NotEqExpr,
    TokenType.T_LESS_THAN: LessExpr,
    TokenType.T_GREATER_THAN: GreaterExpr,
    TokenType.T_LESS_EQUAL_THAN: LessEqExpr,
    TokenType.T_GREATER_EQUAL_THAN: GreaterEqExpr,
    TokenType.T_IN: InExpr,
}

sum_mapper: dict[TokenType, type] = {
    TokenType.T_PLUS: AddExpr,
    TokenType.T_MINUS: SubExpr,
}
