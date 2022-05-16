from enum import Enum, auto

from LexerModule.Tokens import TokenType
from ParserModule.Program import EqExpr, NotEqExpr, LessExpr, GreaterExpr, LessEqExpr, GreaterEqExpr, InExpr, AddExpr, \
    SubExpr, BasicAssignment, AddAssignment, SubAssignment, MulAssignment, DivAssignment, ModAssignment, MulExpr, \
    DivExpr, ModExpr, IntDivExpr


class Operator(Enum):
    pass


# noinspection PyArgumentList
class AssignmentOperator(Operator):
    ASSIGNMENT = auto()
    PLUS_ASSIGNMENT = auto()
    MINUS_ASSIGNMENT = auto()
    MULTIPLY_ASSIGNMENT = auto()
    DIVIDE_ASSIGNMENT = auto()
    MODULUS_ASSIGNMENT = auto()


# noinspection PyArgumentList
class ArithmeticOperator(Operator):
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    INT_DIVIDE = auto()
    MODULUS = auto()


# noinspection PyArgumentList
class LogicOperator(Operator):
    AND = auto()
    OR = auto()
    IN = auto()
    NOT = auto()
    LESS_THAN = auto()
    LESS_EQUAL_THAN = auto()
    GREATER_THAN = auto()
    GREATER_EQUAL_THAN = auto()
    EQUAL = auto()
    NOTEQUAL = auto()


arithmetic_mapper: dict[TokenType, ArithmeticOperator] = {
    TokenType.T_PLUS:                   ArithmeticOperator.PLUS,
    TokenType.T_MINUS:                  ArithmeticOperator.MINUS,
    TokenType.T_MULTIPLY:               ArithmeticOperator.MULTIPLY,
    TokenType.T_DIVIDE:                 ArithmeticOperator.DIVIDE,
    TokenType.T_MODULUS:                ArithmeticOperator.MODULUS,
    TokenType.T_INT_DIVIDE:             ArithmeticOperator.INT_DIVIDE,
}

mul_mapper: dict[TokenType, type] = {
    TokenType.T_MULTIPLY:               MulExpr,
    TokenType.T_DIVIDE:                 DivExpr,
    TokenType.T_MODULUS:                ModExpr,
    TokenType.T_INT_DIVIDE:             IntDivExpr,
}

assignment_mapper: dict[TokenType, type] = {
    TokenType.T_ASSIGNMENT:             BasicAssignment,
    TokenType.T_PLUS_ASSIGNMENT:        AddAssignment,
    TokenType.T_MINUS_ASSIGNMENT:       SubAssignment,
    TokenType.T_MULTIPLY_ASSIGNMENT:    MulAssignment,
    TokenType.T_DIVIDE_ASSIGNMENT:      DivAssignment,
    TokenType.T_MODULUS_ASSIGNMENT:     ModAssignment,
}

comp_mapper: dict[TokenType, type] = {
    TokenType.T_EQUAL:                  EqExpr,
    TokenType.T_NOTEQUAL:               NotEqExpr,
    TokenType.T_LESS_THAN:              LessExpr,
    TokenType.T_GREATER_THAN:           GreaterExpr,
    TokenType.T_LESS_EQUAL_THAN:        LessEqExpr,
    TokenType.T_GREATER_EQUAL_THAN:     GreaterEqExpr,
    TokenType.T_IN:                     InExpr,
}

sum_mapper: dict[TokenType, type] = {
    TokenType.T_PLUS:                   AddExpr,
    TokenType.T_MINUS:                  SubExpr,
}
