class Visited:
    def __init__(self, position: (int, int) = ()):
        self.position = position


class Program(Visited):
    def __init__(self, functions: dict[str, "Function"]) -> None:
        super().__init__((1, 1))
        self.functions = functions

    def accept(self, visitor):
        return visitor.visit_program(self)

    def __repr__(self):
        return f"{type(self).__name__}({self.functions})"

    def __eq__(self, other):
        if self.functions != other.functions:
            return False
        return True


class Function(Visited):
    def __init__(self, name: "Identifier", params: list["Identifier"], statements: "Block",
                 position: (int, int) = ()) -> None:
        super().__init__(position)
        self.name = name
        self.params = params
        self.statements = statements

    def accept(self, visitor):
        return visitor.visit_function(self)

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


class Block(list, Visited):
    def __init__(self, statements: list["Statement"] = (), position: (int, int) = ()) -> None:
        super().__init__(statements)
        self.position = position

    def accept(self, visitor):
        return visitor.visit_block(self)


class Statement(Visited):
    pass


class Assignment(Statement):
    def __init__(self, left_expr: "Expression", right_expr: "Expression", position: (int, int) = ()) -> None:
        super().__init__(position)
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
        return f"{type(self).__name__}({self.left_expr}, {self.right_expr})"


class BasicAssignment(Assignment):
    def __init__(self, left_expr: "Identifier", right_expr: "Expression", position: (int, int) = ()) -> None:
        super().__init__(left_expr, right_expr, position)
        self.operator = '='

    def accept(self, visitor):
        return visitor.visit_basic_assignment(self)


class ModifyingAssignment(Assignment):
    def __init__(self, left_expr: "Expression", right_expr: "Expression", position: (int, int) = ()) -> None:
        super().__init__(left_expr, right_expr, position)

    def accept(self, visitor):
        return visitor.visit_modifying_assignment(self)


class AddAssignment(ModifyingAssignment):
    def __init__(self, left_expr: "Identifier", right_expr: "Expression", position: (int, int) = ()) -> None:
        super().__init__(left_expr, right_expr, position)
        self.operator = '+='


class SubAssignment(ModifyingAssignment):
    def __init__(self, left_expr: "Identifier", right_expr: "Expression", position: (int, int) = ()) -> None:
        super().__init__(left_expr, right_expr, position)
        self.operator = '-='


class MulAssignment(ModifyingAssignment):
    def __init__(self, left_expr: "Identifier", right_expr: "Expression", position: (int, int) = ()) -> None:
        super().__init__(left_expr, right_expr, position)
        self.operator = '*='


class DivAssignment(ModifyingAssignment):
    def __init__(self, left_expr: "Identifier", right_expr: "Expression", position: (int, int) = ()) -> None:
        super().__init__(left_expr, right_expr, position)
        self.operator = '/='


class ModAssignment(ModifyingAssignment):
    def __init__(self, left_expr: "Identifier", right_expr: "Expression", position: (int, int) = ()) -> None:
        super().__init__(left_expr, right_expr, position)
        self.operator = '%='


class ReturnStatement(Statement):
    def __init__(self, values: list["Expression"], position: (int, int) = ()) -> None:
        super().__init__(position)
        self.values = values

    def accept(self, visitor):
        return visitor.visit_return_statement(self)

    def __repr__(self):
        return f"{type(self).__name__}({self.values})"

    def __eq__(self, other):
        if self.values != other.values:
            return False
        return True


class IfStatement(Statement):
    def __init__(self, condition: "Expression", statements: "Block", elif_stmts: list["ElifBlock"],
                 else_stmt: "ElseBlock | None" = None, position: (int, int) = ()) -> None:
        super().__init__(position)
        self.condition = condition
        self.statements = statements
        self.elif_stmts = elif_stmts
        self.else_stmt = else_stmt

    def accept(self, visitor):
        return visitor.visit_if_statement(self)

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


class ElifBlock(Visited):
    def __init__(self, condition: "Expression", statements: "Block", position: (int, int) = ()) -> None:
        super().__init__(position)
        self.condition = condition
        self.statements = statements

    def accept(self, visitor):
        return visitor.visit_elif_block(self)

    def __repr__(self):
        return f"{type(self).__name__}({self.condition}, {self.statements})"

    def __eq__(self, other):
        if self.condition != other.condition:
            return False
        if self.statements != other.statements:
            return False
        return True


class ElseBlock(Block):
    def __init__(self, statements: "Block", position: (int, int) = ()) -> None:
        super().__init__(statements, position)

    def accept(self, visitor):
        return visitor.visit_else_block(self)


class ForStatement(Statement):
    def __init__(self, iterator: "Identifier", iterable: "Expression", statements: "Block",
                 position: (int, int) = ()) -> None:
        super().__init__(position)
        self.iterator = iterator
        self.iterable = iterable
        self.statements = statements

    def accept(self, visitor):
        return visitor.visit_for_statement(self)

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
    def __init__(self, condition: "Expression", statements: "Block", position: (int, int) = ()) -> None:
        super().__init__(position)
        self.condition = condition
        self.statements = statements

    def accept(self, visitor):
        return visitor.visit_while_statement(self)

    def __repr__(self):
        return f"{type(self).__name__}({self.condition}, {self.statements})"

    def __eq__(self, other):
        if self.condition != other.condition:
            return False
        if self.statements != other.statements:
            return False
        return True


class TwoSidedExpression(Statement):
    def __init__(self, left_expr: "Expression", right_expr: "Expression", position: (int, int) = ()) -> None:
        super().__init__(position)
        self.left_expr = left_expr
        self.right_expr = right_expr
        self.operator = None

    def __repr__(self):
        return f"{type(self).__name__}({self.left_expr}, {self.right_expr})"

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
    def __init__(self, left_expr: "Expression", right_expr: "Expression", position: (int, int) = ()) -> None:
        super().__init__(left_expr, right_expr, position)
        self.operator = "or"


class AndExpr(TwoSidedExpression):
    def __init__(self, left_expr: "Expression", right_expr: "Expression", position: (int, int) = ()) -> None:
        super().__init__(left_expr, right_expr, position)
        self.operator = "and"


class EqExpr(TwoSidedExpression):
    def __init__(self, left_expr: "Expression", right_expr: "Expression", position: (int, int) = ()) -> None:
        super().__init__(left_expr, right_expr, position)
        self.operator = "=="


class NotEqExpr(TwoSidedExpression):
    def __init__(self, left_expr: "Expression", right_expr: "Expression", position: (int, int) = ()) -> None:
        super().__init__(left_expr, right_expr, position)
        self.operator = "!="


class LessExpr(TwoSidedExpression):
    def __init__(self, left_expr: "Expression", right_expr: "Expression", position: (int, int) = ()) -> None:
        super().__init__(left_expr, right_expr, position)
        self.operator = "<"


class GreaterExpr(TwoSidedExpression):
    def __init__(self, left_expr: "Expression", right_expr: "Expression", position: (int, int) = ()) -> None:
        super().__init__(left_expr, right_expr, position)
        self.operator = ">"


class LessEqExpr(TwoSidedExpression):
    def __init__(self, left_expr: "Expression", right_expr: "Expression", position: (int, int) = ()) -> None:
        super().__init__(left_expr, right_expr, position)
        self.operator = "<="


class GreaterEqExpr(TwoSidedExpression):
    def __init__(self, left_expr: "Expression", right_expr: "Expression", position: (int, int) = ()) -> None:
        super().__init__(left_expr, right_expr, position)
        self.operator = ">="


class InExpr(TwoSidedExpression):
    def __init__(self, left_expr: "Expression", right_expr: "Expression", position: (int, int) = ()) -> None:
        super().__init__(left_expr, right_expr, position)
        self.operator = "in"


class AddExpr(TwoSidedExpression):
    def __init__(self, left_expr: "Expression", right_expr: "Expression", position: (int, int) = ()) -> None:
        super().__init__(left_expr, right_expr, position)
        self.operator = "+"


class SubExpr(TwoSidedExpression):
    def __init__(self, left_expr: "Expression", right_expr: "Expression", position: (int, int) = ()) -> None:
        super().__init__(left_expr, right_expr, position)
        self.operator = "-"


class MulExpr(TwoSidedExpression):
    def __init__(self, left_expr: "Expression", right_expr: "Expression", position: (int, int) = ()) -> None:
        super().__init__(left_expr, right_expr, position)
        self.operator = "*"


class DivExpr(TwoSidedExpression):
    def __init__(self, left_expr: "Expression", right_expr: "Expression", position: (int, int) = ()) -> None:
        super().__init__(left_expr, right_expr, position)
        self.operator = "/"


class ModExpr(TwoSidedExpression):
    def __init__(self, left_expr: "Expression", right_expr: "Expression", position: (int, int) = ()) -> None:
        super().__init__(left_expr, right_expr, position)
        self.operator = "%"


class IntDivExpr(TwoSidedExpression):
    def __init__(self, left_expr: "Expression", right_expr: "Expression", position: (int, int) = ()) -> None:
        super().__init__(left_expr, right_expr, position)
        self.operator = "//"


class OneSidedExpression(Statement):
    def __init__(self, value: "Expression", position: (int, int) = ()) -> None:
        super().__init__(position)
        self.value = value
        self.operator = None

    def __repr__(self):
        return f"{type(self).__name__}({self.value})"

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
        super().__init__(value, value.position)
        self.operator = "-"


class Negate(OneSidedExpression):
    def __init__(self, value: "Expression", position: (int, int) = ()) -> None:
        super().__init__(value, position)
        self.operator = "not"


class Assignable:
    pass


class DotOperator(TwoSidedExpression, Assignable):
    def __init__(self, left_expr: "Expression", right_expr: "Expression", position: (int, int) = ()) -> None:
        super().__init__(left_expr, right_expr, position)
        self.operator = "."

    def accept(self, visitor):
        return visitor.visit_dot_operator(self)


class FunCall(TwoSidedExpression, Assignable):
    def __repr__(self):
        return f"{type(self).__name__}({self.left_expr}, {self.right_expr})"

    def accept(self, visitor):
        return visitor.visit_fun_call(self)


class ListElement(TwoSidedExpression, Assignable):
    def accept(self, visitor):
        return visitor.visit_list_element(self)


class Atom(Statement):
    def __init__(self, value: "Expression | list[Expression] | str | int | bool | None",
                 position: (int, int) = ()) -> None:
        super().__init__(position)
        self.value = value

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.value})"

    def __eq__(self, other) -> bool:
        if self.value != other.value:
            return False
        return True

    def accept(self, visitor):
        return visitor.visit_atom(self)


class List(Atom):
    def __init__(self, value: list["Expression"], position: (int, int) = ()) -> None:
        super().__init__(value, position)

    def accept(self, visitor):
        return visitor.visit_list(self)


class String(Atom):
    def __init__(self, value: str, position: (int, int) = ()) -> None:
        super().__init__(value, position)

    def __repr__(self):
        return f"{type(self).__name__}(\"{self.value}\")"


class Integer(Atom):
    def __init__(self, value: int, position: (int, int) = ()) -> None:
        super().__init__(value, position)


class Boolean(Atom):
    def __init__(self, value: bool, position: (int, int) = ()) -> None:
        super().__init__(value, position)


class Null(Atom):
    def __init__(self, position: (int, int) = ()) -> None:
        super().__init__(None, position)

    def __repr__(self):
        return f"{type(self).__name__}()"


class Identifier(Atom, Assignable):
    def __init__(self, value: str, position: (int, int) = ()) -> None:
        super().__init__(value, position)

    def __repr__(self):
        return f"{type(self).__name__}(\"{self.value}\")"

    def accept(self, visitor):
        return visitor.visit_identifier(self)


Expression = OneSidedExpression | TwoSidedExpression | Atom | list["Expression"]
