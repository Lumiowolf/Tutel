class Program:
    def __init__(self, functions: dict[str, "Function"]) -> None:
        self.functions = functions

    def __repr__(self):
        return f"{type(self).__name__}({self.functions})"

    def __eq__(self, other):
        if self.functions != other.functions:
            return False
        return True


class Function:
    def __init__(self, name: "Identifier", params: list["Identifier"], statements: list["Statement"]) -> None:
        self.name = name
        self.params = params
        self.statements = statements

    def __repr__(self):
        return f"{type(self).__name__}({self.name}, {self.params}, {self.statements})"

    def __eq__(self, other):
        if self.name != other.name:
            return False
        if self.params != other.params:
            return False
        if self.statements != other.statements:
            return False
        return True


class Block(list):
    def __init__(self, statements: list["Statement"] = ()) -> None:
        super().__init__(statements)


class Statement:
    pass


class Assignment(Statement):
    def __init__(self, left_expr: "Expression", right_expr: "Expression") -> None:
        self.left_expr = left_expr
        self.right_expr = right_expr

    def __eq__(self, other):
        if self.left_expr != other.left_expr:
            return False
        if self.right_expr != other.right_expr:
            return False
        return True

    def __repr__(self):
        return f"{type(self).__name__}({self.left_expr}, {self.right_expr})"


class BasicAssignment(Assignment):
    def __init__(self, left_expr: "Identifier", right_expr: "Expression") -> None:
        super().__init__(left_expr, right_expr)
        self.operator = '='


class AddAssignment(Assignment):
    def __init__(self, left_expr: "Identifier", right_expr: "Expression") -> None:
        super().__init__(left_expr, right_expr)
        self.operator = '+='


class SubAssignment(Assignment):
    def __init__(self, left_expr: "Identifier", right_expr: "Expression") -> None:
        super().__init__(left_expr, right_expr)
        self.operator = '-='


class MulAssignment(Assignment):
    def __init__(self, left_expr: "Identifier", right_expr: "Expression") -> None:
        super().__init__(left_expr, right_expr)
        self.operator = '*='


class DivAssignment(Assignment):
    def __init__(self, left_expr: "Identifier", right_expr: "Expression") -> None:
        super().__init__(left_expr, right_expr)
        self.operator = '/='


class ModAssignment(Assignment):
    def __init__(self, left_expr: "Identifier", right_expr: "Expression") -> None:
        super().__init__(left_expr, right_expr)
        self.operator = '%='


class ReturnStatement(Statement):
    def __init__(self, values: list["Expression"]) -> None:
        self.values = values

    def __repr__(self):
        return f"{type(self).__name__}({self.values})"

    def __eq__(self, other):
        if self.values != other.values:
            return False
        return True


class IfStatement(Statement):
    def __init__(self,
                 condition: "Expression",
                 statements: list["Statement"],
                 elif_stmts: list["ElifBlock"],
                 else_stmt: "ElseBlock | None" = None) -> None:
        self.condition = condition
        self.statements = statements
        self.elif_stmts = elif_stmts
        self.else_stmt = else_stmt

    def __repr__(self):
        return f"{type(self).__name__}({self.condition}, {self.statements}, {self.elif_stmts}, {self.else_stmt})"

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


class ElifBlock:
    def __init__(self,
                 condition: "Expression",
                 statements: list["Statement"]) -> None:
        self.condition = condition
        self.statements = statements

    def __repr__(self):
        return f"{type(self).__name__}({self.condition}, {self.statements})"

    def __eq__(self, other):
        if self.condition != other.condition:
            return False
        if self.statements != other.statements:
            return False
        return True


class ElseBlock:
    def __init__(self, statements: list["Statement"]) -> None:
        self.statements = statements

    def __repr__(self):
        return f"{type(self).__name__}({self.statements})"

    def __eq__(self, other):
        if self.statements != other.statements:
            return False
        return True


class ForStatement(Statement):
    def __init__(self, iterator: "Identifier", iterable: "Expression", statements: list["Statement"]) -> None:
        self.iterator = iterator
        self.iterable = iterable
        self.statements = statements

    def __repr__(self):
        return f"{type(self).__name__}({self.iterator}, {self.iterable}, {self.statements})"

    def __eq__(self, other):
        if self.iterator != other.iterator:
            return False
        if self.iterable != other.iterable:
            return False
        if self.statements != other.statements:
            return False
        return True


class WhileStatement(Statement):
    def __init__(self, condition: "Expression", statements: list["Statement"]) -> None:
        self.condition = condition
        self.statements = statements

    def __repr__(self):
        return f"{type(self).__name__}({self.condition}, {self.statements})"

    def __eq__(self, other):
        if self.condition != other.condition:
            return False
        if self.statements != other.statements:
            return False
        return True


class TwoSidedExpression(Statement):
    def __init__(self, left_expr: "Expression",
                 right_expr: "Expression") -> None:
        self.left_expr = left_expr
        self.right_expr = right_expr

    def __repr__(self):
        return f"{type(self).__name__}({self.left_expr}, {self.right_expr})"

    def __eq__(self, other):
        if self.left_expr != other.left_expr:
            return False
        if self.right_expr != other.right_expr:
            return False
        return True


class OrExpr(TwoSidedExpression):
    pass


class AndExpr(TwoSidedExpression):
    pass


class InvertExpr(TwoSidedExpression):
    pass


class EqExpr(TwoSidedExpression):
    pass


class NotEqExpr(TwoSidedExpression):
    pass


class LessExpr(TwoSidedExpression):
    pass


class GreaterExpr(TwoSidedExpression):
    pass


class LessEqExpr(TwoSidedExpression):
    pass


class GreaterEqExpr(TwoSidedExpression):
    pass


class InExpr(TwoSidedExpression):
    pass


class AddExpr(TwoSidedExpression):
    pass


class SubExpr(TwoSidedExpression):
    pass


class MulExpr(TwoSidedExpression):
    pass


class DivExpr(TwoSidedExpression):
    pass


class ModExpr(TwoSidedExpression):
    pass


class IntDivExpr(TwoSidedExpression):
    pass


class DotOperator(TwoSidedExpression):
    pass


class FunCall(TwoSidedExpression):
    def __repr__(self):
        return f"{type(self).__name__}({self.left_expr}, {self.right_expr})"


class ListElement(TwoSidedExpression):
    pass


class Atom(Statement):
    def __init__(self, value: "Expression | list[Expression] | str | int | bool | None") -> None:
        self.value = value

    def __repr__(self):
        return f"{type(self).__name__}({self.value})"

    def __eq__(self, other):
        if self.value != other.value:
            return False
        return True


class Negate(Atom):
    def __init__(self, value: "Expression") -> None:
        super().__init__(value)


class List(Atom):
    def __init__(self, value: list["Expression"]) -> None:
        super().__init__(value)


class String(Atom):
    def __init__(self, value: str) -> None:
        super().__init__(value)

    def __repr__(self):
        return f"{type(self).__name__}(\"{self.value}\")"


class Integer(Atom):
    def __init__(self, value: int) -> None:
        super().__init__(value)


class Boolean(Atom):
    def __init__(self, value: bool) -> None:
        super().__init__(value)


class Null(Atom):
    def __init__(self) -> None:
        super().__init__(None)

    def __repr__(self):
        return f"{type(self).__name__}()"


class Identifier(Atom):
    def __init__(self, value: str) -> None:
        super().__init__(value)

    def __repr__(self):
        return f"{type(self).__name__}(\"{self.value}\")"


Expression = TwoSidedExpression | Atom | list["Expression"]
