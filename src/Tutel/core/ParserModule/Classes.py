class Visited:
    def __init__(self, lineno: int):
        self.lineno = lineno

    def accept(self, visitor):
        pass


class Program(Visited):
    def __init__(self, functions: dict[str, "Function"], lineno: int, main: str = "main") -> None:
        super().__init__(lineno)
        self.functions = functions
        self.main = main

    def accept(self, visitor):
        return visitor.visit_program(self)

    def __repr__(self):
        return f"{type(self).__name__}({self.functions}, lineno={self.lineno})"

    def __eq__(self, other):
        if self.functions != other.functions:
            return False
        return True


class Function(Visited):
    def __init__(self, name: "Identifier", params: list["Identifier"], statements: "Block",
                 lineno: int) -> None:
        super().__init__(lineno)
        self.name = name
        self.params = params
        self.statements = statements

    def accept(self, visitor):
        return visitor.visit_function(self)

    def __repr__(self):
        return f"{type(self).__name__}({self.name}, {self.params}, {self.statements}, lineno={self.lineno})"

    def __eq__(self, other):
        if self.name != other.name:
            return False
        if self.params != other.params:
            return False
        if self.statements != other.statements:
            return False
        return True


class Block(list, Visited):
    def __init__(self, statements: list["Statement"], lineno: int) -> None:
        super().__init__(statements)
        self.lineno = lineno

    def accept(self, visitor):
        return visitor.visit_block(self)


class Statement(Visited):
    pass


class Assignment(Statement):
    def __init__(self, left_expr: "Expression", right_expr: "Expression", lineno: int) -> None:
        super().__init__(lineno)
        self.left_expr = left_expr
        self.right_expr = right_expr
        self.operator = None

    def __eq__(self, other):
        if self.left_expr != other.left_expr:
            return False
        if self.right_expr != other.right_expr:
            return False
        return True

    def __repr__(self):
        return f"{type(self).__name__}({self.left_expr}, {self.right_expr}, lineno={self.lineno})"


class BasicAssignment(Assignment):
    def __init__(self, left_expr: "Identifier", right_expr: "Expression", lineno: int) -> None:
        super().__init__(left_expr, right_expr, lineno)
        self.operator = '='

    def accept(self, visitor):
        return visitor.visit_basic_assignment(self)


class ModifyingAssignment(Assignment):
    def __init__(self, left_expr: "Expression", right_expr: "Expression", lineno: int) -> None:
        super().__init__(left_expr, right_expr, lineno)

    def accept(self, visitor):
        return visitor.visit_modifying_assignment(self)


class AddAssignment(ModifyingAssignment):
    def __init__(self, left_expr: "Identifier", right_expr: "Expression", lineno: int) -> None:
        super().__init__(left_expr, right_expr, lineno)
        self.operator = '+='


class SubAssignment(ModifyingAssignment):
    def __init__(self, left_expr: "Identifier", right_expr: "Expression", lineno: int) -> None:
        super().__init__(left_expr, right_expr, lineno)
        self.operator = '-='


class MulAssignment(ModifyingAssignment):
    def __init__(self, left_expr: "Identifier", right_expr: "Expression", lineno: int) -> None:
        super().__init__(left_expr, right_expr, lineno)
        self.operator = '*='


class DivAssignment(ModifyingAssignment):
    def __init__(self, left_expr: "Identifier", right_expr: "Expression", lineno: int) -> None:
        super().__init__(left_expr, right_expr, lineno)
        self.operator = '/='


class ModAssignment(ModifyingAssignment):
    def __init__(self, left_expr: "Identifier", right_expr: "Expression", lineno: int) -> None:
        super().__init__(left_expr, right_expr, lineno)
        self.operator = '%='


class ReturnStatement(Statement):
    def __init__(self, values: list["Expression"], lineno: int) -> None:
        super().__init__(lineno)
        self.values = values

    def accept(self, visitor):
        return visitor.visit_return_statement(self)

    def __repr__(self):
        return f"{type(self).__name__}({self.values}, lineno={self.lineno})"

    def __eq__(self, other):
        if self.values != other.values:
            return False
        return True


class IfStatement(Statement):
    def __init__(self, condition: "Expression", statements: "Block", elif_stmts: list["ElifBlock"],
                 else_stmt: "ElseBlock | None", lineno: int) -> None:
        super().__init__(lineno)
        self.condition = condition
        self.statements = statements
        self.elif_stmts = elif_stmts
        self.else_stmt = else_stmt

    def accept(self, visitor):
        return visitor.visit_if_statement(self)

    def __repr__(self):
        return f"{type(self).__name__}({self.condition}, {self.statements}, {self.elif_stmts}, {self.else_stmt}, lineno={self.lineno})"

    def __eq__(self, other):
        if self.condition != other.condition:
            return False
        if self.statements != other.statements:
            return False
        if not all([self.elif_stmts, other.elif_stmts]) and any([self.elif_stmts, other.elif_stmts]):
            return False
        if self.elif_stmts != other.elif_stmts:
            return False
        if not all([self.else_stmt, other.else_stmt]) and any([self.else_stmt, other.else_stmt]):
            return False
        if self.else_stmt != other.else_stmt:
            return False
        return True


class ElifBlock(Visited):
    def __init__(self, condition: "Expression", statements: "Block", lineno: int) -> None:
        super().__init__(lineno)
        self.condition = condition
        self.statements = statements

    def accept(self, visitor):
        return visitor.visit_elif_block(self)

    def __repr__(self):
        return f"{type(self).__name__}({self.condition}, {self.statements}, lineno={self.lineno})"

    def __eq__(self, other):
        if self.condition != other.condition:
            return False
        if self.statements != other.statements:
            return False
        return True


class ElseBlock(Block):
    def __init__(self, statements: "Block", lineno: int) -> None:
        super().__init__(statements, lineno)

    def accept(self, visitor):
        return visitor.visit_else_block(self)


class ForStatement(Statement):
    def __init__(self, iterator: "Identifier", iterable: "Expression", statements: "Block",
                 lineno: int) -> None:
        super().__init__(lineno)
        self.iterator = iterator
        self.iterable = iterable
        self.statements = statements

    def accept(self, visitor):
        return visitor.visit_for_statement(self)

    def __repr__(self):
        return f"{type(self).__name__}({self.iterator}, {self.iterable}, {self.statements}, lineno={self.lineno})"

    def __eq__(self, other):
        if self.iterator != other.iterator:
            return False
        if self.iterable != other.iterable:
            return False
        if self.statements != other.statements:
            return False
        return True


class WhileStatement(Statement):
    def __init__(self, condition: "Expression", statements: "Block", lineno: int) -> None:
        super().__init__(lineno)
        self.condition = condition
        self.statements = statements

    def accept(self, visitor):
        return visitor.visit_while_statement(self)

    def __repr__(self):
        return f"{type(self).__name__}({self.condition}, {self.statements}, lineno={self.lineno})"

    def __eq__(self, other):
        if self.condition != other.condition:
            return False
        if self.statements != other.statements:
            return False
        return True


class TwoSidedExpression(Statement):
    def __init__(self, left_expr: "Expression", right_expr: "Expression", lineno: int) -> None:
        super().__init__(lineno)
        self.left_expr = left_expr
        self.right_expr = right_expr
        self.operator = None

    def __repr__(self):
        return f"{type(self).__name__}({self.left_expr}, {self.right_expr}, lineno={self.lineno})"

    def __eq__(self, other):
        if self.left_expr != other.left_expr:
            return False
        if self.right_expr != other.right_expr:
            return False
        if self.operator != other.operator:
            return False
        return True

    def accept(self, visitor):
        return visitor.visit_two_sided_expression(self)


class OrExpr(TwoSidedExpression):
    def __init__(self, left_expr: "Expression", right_expr: "Expression", lineno: int) -> None:
        super().__init__(left_expr, right_expr, lineno)
        self.operator = "or"


class AndExpr(TwoSidedExpression):
    def __init__(self, left_expr: "Expression", right_expr: "Expression", lineno: int) -> None:
        super().__init__(left_expr, right_expr, lineno)
        self.operator = "and"


class EqExpr(TwoSidedExpression):
    def __init__(self, left_expr: "Expression", right_expr: "Expression", lineno: int) -> None:
        super().__init__(left_expr, right_expr, lineno)
        self.operator = "=="


class NotEqExpr(TwoSidedExpression):
    def __init__(self, left_expr: "Expression", right_expr: "Expression", lineno: int) -> None:
        super().__init__(left_expr, right_expr, lineno)
        self.operator = "!="


class LessExpr(TwoSidedExpression):
    def __init__(self, left_expr: "Expression", right_expr: "Expression", lineno: int) -> None:
        super().__init__(left_expr, right_expr, lineno)
        self.operator = "<"


class GreaterExpr(TwoSidedExpression):
    def __init__(self, left_expr: "Expression", right_expr: "Expression", lineno: int) -> None:
        super().__init__(left_expr, right_expr, lineno)
        self.operator = ">"


class LessEqExpr(TwoSidedExpression):
    def __init__(self, left_expr: "Expression", right_expr: "Expression", lineno: int) -> None:
        super().__init__(left_expr, right_expr, lineno)
        self.operator = "<="


class GreaterEqExpr(TwoSidedExpression):
    def __init__(self, left_expr: "Expression", right_expr: "Expression", lineno: int) -> None:
        super().__init__(left_expr, right_expr, lineno)
        self.operator = ">="


class InExpr(TwoSidedExpression):
    def __init__(self, left_expr: "Expression", right_expr: "Expression", lineno: int) -> None:
        super().__init__(left_expr, right_expr, lineno)
        self.operator = "in"


class AddExpr(TwoSidedExpression):
    def __init__(self, left_expr: "Expression", right_expr: "Expression", lineno: int) -> None:
        super().__init__(left_expr, right_expr, lineno)
        self.operator = "+"


class SubExpr(TwoSidedExpression):
    def __init__(self, left_expr: "Expression", right_expr: "Expression", lineno: int) -> None:
        super().__init__(left_expr, right_expr, lineno)
        self.operator = "-"


class MulExpr(TwoSidedExpression):
    def __init__(self, left_expr: "Expression", right_expr: "Expression", lineno: int) -> None:
        super().__init__(left_expr, right_expr, lineno)
        self.operator = "*"


class DivExpr(TwoSidedExpression):
    def __init__(self, left_expr: "Expression", right_expr: "Expression", lineno: int) -> None:
        super().__init__(left_expr, right_expr, lineno)
        self.operator = "/"


class ModExpr(TwoSidedExpression):
    def __init__(self, left_expr: "Expression", right_expr: "Expression", lineno: int) -> None:
        super().__init__(left_expr, right_expr, lineno)
        self.operator = "%"


class IntDivExpr(TwoSidedExpression):
    def __init__(self, left_expr: "Expression", right_expr: "Expression", lineno: int) -> None:
        super().__init__(left_expr, right_expr, lineno)
        self.operator = "//"


class OneSidedExpression(Statement):
    def __init__(self, value: "Expression", lineno: int) -> None:
        super().__init__(lineno)
        self.value = value
        self.operator = None

    def __repr__(self):
        return f"{type(self).__name__}({self.value}, lineno={self.lineno})"

    def __eq__(self, other):
        if self.value != other.value:
            return False
        if self.operator != other.operator:
            return False
        return True

    def accept(self, visitor):
        return visitor.visit_one_sided_expression(self)


class InvertExpr(OneSidedExpression):
    def __init__(self, value: "Expression") -> None:
        super().__init__(value, value.lineno)
        self.operator = "-"


class Negate(OneSidedExpression):
    def __init__(self, value: "Expression", lineno: int) -> None:
        super().__init__(value, lineno)
        self.operator = "not"


class Assignable:
    pass


class DotOperator(TwoSidedExpression, Assignable):
    def __init__(self, left_expr: "Expression", right_expr: "Expression", lineno: int) -> None:
        super().__init__(left_expr, right_expr, lineno)
        self.operator = "."

    def accept(self, visitor):
        return visitor.visit_dot_operator(self)


class FunCall(TwoSidedExpression, Assignable):
    def __repr__(self):
        return f"{type(self).__name__}({self.left_expr}, {self.right_expr}, lineno={self.lineno})"

    def accept(self, visitor):
        return visitor.visit_fun_call(self)


class ListElement(TwoSidedExpression, Assignable):
    def accept(self, visitor):
        return visitor.visit_list_element(self)


class Atom(Statement):
    def __init__(self, value: "Expression | list[Expression] | str | int | bool | None",
                 lineno: int) -> None:
        super().__init__(lineno)
        self.value = value

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.value}, lineno={self.lineno})"

    def __eq__(self, other) -> bool:
        if self.value != other.value:
            return False
        return True

    def accept(self, visitor):
        return visitor.visit_atom(self)


class List(Atom):
    def __init__(self, value: list["Expression"], lineno: int) -> None:
        super().__init__(value, lineno)

    def accept(self, visitor):
        return visitor.visit_list(self)


class String(Atom):
    def __init__(self, value: str, lineno: int) -> None:
        super().__init__(value, lineno)

    def __repr__(self):
        return f"{type(self).__name__}(\"{self.value}\", lineno={self.lineno})"


class Integer(Atom):
    def __init__(self, value: int, lineno: int) -> None:
        super().__init__(value, lineno)


class Boolean(Atom):
    def __init__(self, value: bool, lineno: int) -> None:
        super().__init__(value, lineno)


class Null(Atom):
    def __init__(self, lineno: int) -> None:
        super().__init__(None, lineno)

    def __repr__(self):
        return f"{type(self).__name__}(lineno={self.lineno})"


class Identifier(Atom, Assignable):
    def __init__(self, value: str, lineno: int) -> None:
        super().__init__(value, lineno)

    def __repr__(self):
        return f"{type(self).__name__}(\"{self.value}\", lineno={self.lineno})"

    def accept(self, visitor):
        return visitor.visit_identifier(self)


Expression = OneSidedExpression | TwoSidedExpression | Atom | list["Expression"]
