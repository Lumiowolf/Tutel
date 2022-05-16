class Program:
    def __init__(self, functions: dict[str, "Function"]) -> None:
        self.functions = functions

    def __repr__(self):
        return f"{type(self).__name__}[{self.functions}]"

    def __eq__(self, other):
        if self.functions != other.functions:
            return False
        return True


class Function:
    def __init__(self, params: list["Identifier"], statements: list["Statement"]) -> None:
        self.params = params
        self.statements = statements

    def __repr__(self):
        return f"{type(self).__name__}[params: {self.params}; statements: {self.statements}]"

    def __eq__(self, other):
        if self.params != other.params:
            return False
        if self.statements != other.statements:
            return False
        return True


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


class BasicAssignment(Assignment):
    def __init__(self, left_expr: "Identifier", right_expr: "Expression") -> None:
        super().__init__(left_expr, right_expr)
        self.operator = '='

    def __repr__(self):
        return f"{type(self).__name__}[{self.left_expr} = {self.right_expr}]"


class AddAssignment(Assignment):
    def __init__(self, left_expr: "Identifier", right_expr: "Expression") -> None:
        super().__init__(left_expr, right_expr)
        self.operator = '+'

    def __repr__(self):
        return f"{type(self).__name__}[{self.left_expr} + {self.right_expr}]"


class SubAssignment(Assignment):
    def __init__(self, left_expr: "Identifier", right_expr: "Expression") -> None:
        super().__init__(left_expr, right_expr)
        self.operator = '-'

    def __repr__(self):
        return f"{type(self).__name__}[{self.left_expr} - {self.right_expr}]"


class MulAssignment(Assignment):
    def __init__(self, left_expr: "Identifier", right_expr: "Expression") -> None:
        super().__init__(left_expr, right_expr)
        self.operator = '*'

    def __repr__(self):
        return f"{type(self).__name__}[{self.left_expr} * {self.right_expr}]"


class DivAssignment(Assignment):
    def __init__(self, left_expr: "Identifier", right_expr: "Expression") -> None:
        super().__init__(left_expr, right_expr)
        self.operator = '/'

    def __repr__(self):
        return f"{type(self).__name__}[{self.left_expr} / {self.right_expr}]"


class ModAssignment(Assignment):
    def __init__(self, left_expr: "Identifier", right_expr: "Expression") -> None:
        super().__init__(left_expr, right_expr)
        self.operator = '%'

    def __repr__(self):
        return f"{type(self).__name__}[{self.left_expr} % {self.right_expr}]"


class ReturnStatement(Statement):
    def __init__(self, values: list["Expression"]) -> None:
        self.values = values

    def __repr__(self):
        return f"{type(self).__name__}[{self.values}]"

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
        return f"{type(self).__name__}[condition: {self.condition}; statements: {self.statements}; " \
               f"elif: {self.elif_stmts}; else: {self.else_stmt}]"

    def __eq__(self, other):
        if self.condition != other.condition:
            return False
        if self.statements != other.statements:
            return False
        if self.elif_stmts != other.elif_stmts:
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
        return f"{type(self).__name__}[condition: {self.condition}; statements: {self.statements}]"

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
        return f"{type(self).__name__}[statements: {self.statements}]"

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
        return f"{type(self).__name__}[iterator: {self.iterator}; " \
               f"iterable: {self.iterable}; statements: {self.statements}]"

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
        return f"{type(self).__name__}[condition: {self.condition}; statements: {self.statements}]"

    def __eq__(self, other):
        if self.condition != other.condition:
            return False
        if self.statements != other.statements:
            return False
        return True


class Expression(Statement):
    def __init__(self, left_expr: "Expression | list[Expression] | str | int | None",
                 right_expr: "Expression | list[Expression] | str | int | None") -> None:
        self.left_expr = left_expr
        self.right_expr = right_expr

    def __repr__(self):
        return f"{type(self).__name__}[left_expr: {self.left_expr}; right_expr: {self.right_expr}]"

    def __eq__(self, other):
        if self.left_expr != other.left_expr:
            return False
        if self.right_expr != other.right_expr:
            return False
        return True


class NegateExpression(Expression):
    def __init__(self, expression: "Expression") -> None:
        super().__init__(expression.left_expr, expression.right_expr)


class OrExpr(Expression):
    pass


class AndExpr(Expression):
    pass


class InvertExpr(Expression):
    pass


class EqExpr(Expression):
    pass


class NotEqExpr(Expression):
    pass


class LessExpr(Expression):
    pass


class GreaterExpr(Expression):
    pass


class LessEqExpr(Expression):
    pass


class GreaterEqExpr(Expression):
    pass


class InExpr(Expression):
    pass


class AddExpr(Expression):
    pass


class SubExpr(Expression):
    pass


class MulExpr(Expression):
    pass


class DivExpr(Expression):
    pass


class ModExpr(Expression):
    pass


class IntDivExpr(Expression):
    pass


class DotOperator(Expression):
    pass


class FunCall(Expression):
    def __repr__(self):
        return f"{type(self).__name__}[fun_name: {self.left_expr}; args: {self.right_expr}]"


class ListElement(Expression):
    pass


class Atom(Expression):
    def __init__(self, expression: "Expression | list[Expression] | str | int | bool | None") -> None:
        super().__init__(expression, None)

    def __repr__(self):
        return f"{type(self).__name__}[{self.left_expr}]"


class Parenthesis(Expression):
    def __init__(self, expression: "Expression") -> None:
        super().__init__(expression.left_expr, expression.right_expr)


class List(Atom):
    def __init__(self, list: list["Expression"]) -> None:
        super().__init__(list)


class String(Atom):
    def __init__(self, string: str) -> None:
        super().__init__(string)


class Integer(Atom):
    def __init__(self, integer: int) -> None:
        super().__init__(integer)


class BoolFalse(Atom):
    def __init__(self) -> None:
        super().__init__(False)

    def __repr__(self):
        return f"{type(self).__name__}"


class BoolTrue(Atom):
    def __init__(self) -> None:
        super().__init__(True)

    def __repr__(self):
        return f"{type(self).__name__}"


class Null(Atom):
    def __init__(self) -> None:
        super().__init__(None)

    def __repr__(self):
        return f"{type(self).__name__}"


class Identifier(Expression):
    def __init__(self, name: str) -> None:
        super().__init__(None, None)
        self.name = name

    def __repr__(self):
        return f"{type(self).__name__}[{self.name}]"

    def __eq__(self, other):
        if self.name != other.name:
            return False
        return True
