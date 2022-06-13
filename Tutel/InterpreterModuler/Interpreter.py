from inspect import signature
from time import sleep

from Tutel.ErrorHandlerModule.ErrorHandler import ErrorHandler
from Tutel.ErrorHandlerModule.ErrorType import LexerException, ParserException, InterpreterException, \
    MismatchedArgsCountException, OutOfRangeException, UnknownException, NothingToRunException, Exit, RecursionException
from Tutel.ErrorHandlerModule.ErrorType import NotIterableException, CannotAssignException, NotDefinedException, \
    UnsupportedOperandException, BadOperandForUnaryException, AttributeException
from Tutel.InterpreterModuler.Variable import Variable, Value
from Tutel.LexerModule.Lexer import Lexer
from Tutel.ParserModule import Classes
from Tutel.ParserModule.Parser import Parser
from Tutel.InterpreterModuler.TutelBuiltins import Turtle, Position, Orientation, Color


class Interpreter:
    def __init__(self, error_handler: ErrorHandler) -> None:
        Value.values = []
        self.running = False
        self.error_handler = error_handler
        self.program = None
        self.start_with = None
        self.start_with_fun = None
        self.function_context: list[list[dict[str, Variable]]] = []
        self.return_flag = False
        self.last_returned = None
        self.evaluate = True
        self.must_exist = True
        self.do_else = True
        self.call_stack = []
        self.obj_visit_map = {
            "Program": self.visit_program,
            "Function": self.visit_function,
            "Block": self.visit_block,
            "Negate": self.visit_negate,
            "List": self.visit_list,
            "String": self.visit_atom,
            "Integer": self.visit_atom,
            "Boolean": self.visit_atom,
            "Null": self.visit_atom,
            "Identifier": self.visit_identifier,
            "IfStatement": self.visit_if_statement,
            "ElifBlock": self.visit_elif_block,
            "ElseBlock": self.visit_else_block,
            "ForStatement": self.visit_for_statement,
            "WhileStatement": self.visit_while_statement,
            "BasicAssignment": self.visit_basic_assignment,
            "AddAssignment": self.visit_modifying_assignment,
            "SubAssignment": self.visit_modifying_assignment,
            "MulAssignment": self.visit_modifying_assignment,
            "DivAssignment": self.visit_modifying_assignment,
            "ModAssignment": self.visit_modifying_assignment,
            "OrExpr": self.visit_two_sided_expression,
            "AndExpr": self.visit_two_sided_expression,
            "InvertExpr": self.visit_invert_expression,
            "EqExpr": self.visit_two_sided_expression,
            "NotEqExpr": self.visit_two_sided_expression,
            "LessExpr": self.visit_two_sided_expression,
            "GreaterExpr": self.visit_two_sided_expression,
            "LessEqExpr": self.visit_two_sided_expression,
            "GreaterEqExpr": self.visit_two_sided_expression,
            "InExpr": self.visit_two_sided_expression,
            "AddExpr": self.visit_two_sided_expression,
            "SubExpr": self.visit_two_sided_expression,
            "MulExpr": self.visit_two_sided_expression,
            "DivExpr": self.visit_two_sided_expression,
            "ModExpr": self.visit_two_sided_expression,
            "IntDivExpr": self.visit_two_sided_expression,
            "DotOperator": self.visit_dot_operator,
            "FunCall": self.visit_fun_call,
            "ListElement": self.visit_list_element,
            "ReturnStatement": self.visit_return_statement,
        }

    def execute(self, program: Classes.Program, start_with: str = None):
        self.running = True
        self.program = program
        if len(self.program.functions) == 0:
            self.error_handler.handle_error(NothingToRunException())
        self.start_with = start_with
        try:
            self.visit(program)
        except RecursionError:
            self.error_handler.handle_error(RecursionException())

    def stop(self):
        self.running = False

    def _get_value(self, var):
        for i in range(len(self.function_context[-1]) - 1, -1, -1):
            for name in self.function_context[-1][i]:
                if name == var:
                    return self.function_context[-1][i][name]
        if var in globals():
            return Value(globals()[var])
        return None

    def _add_function_context(self):
        self.function_context.append([])

    def _add_context(self):
        self.function_context[-1].append({})

    def _drop_context(self):
        self.function_context[-1] = self.function_context[-1][:-1]

    def _drop_function_context(self):
        self.function_context = self.function_context[:-1]

    def _set_local_var(self, name: str, value: Value | Variable):
        if type(value) == Variable:
            value = Value(value.value)
        elif type(value) != Value:
            value = Value(value)
        self.function_context[-1][-1][name] = Variable(name, value)
        return value

    def _is_assignable(self, obj):
        return issubclass(obj.__class__, Classes.Assignable)

    def visit(self, obj: Classes.Visited):
        if self.running:
            return self.obj_visit_map[obj.__class__.__name__](obj)
        self.error_handler.handle_error(Exit())

    def visit_program(self, obj: Classes.Program):
        if self.start_with is None:
            self.start_with_fun = list(obj.functions.values())[0]
        elif self.start_with in obj.functions.keys():
            self.start_with_fun = obj.functions[self.start_with]
        else:
            self.error_handler.handle_error(NotDefinedException(name=self.start_with))
        self._add_function_context()
        self._add_context()
        self.start_with_fun.accept(self)
        self._drop_context()
        self._drop_function_context()

    def visit_function(self, obj: Classes.Function):
        obj.statements.accept(self)
        self.return_flag = False

    def visit_block(self, obj: Classes.Block):
        for statement in obj:
            statement.accept(self)
            if self.return_flag:
                break

    def visit_atom(self, obj: Classes.Atom):
        return Value(obj.value)

    def visit_identifier(self, obj: Classes.Identifier):
        if self.evaluate:
            if (var := self._get_value(obj.value)) is None:
                self.error_handler.handle_error(NotDefinedException(name=f"{obj.value}"))
            return var
        else:
            return obj.value

    def visit_negate(self, obj: Classes.Negate):
        return not obj.value.accept(self)

    def visit_list(self, obj: Classes.List):
        return Value([el.accept(self) for el in obj.value])

    def visit_if_statement(self, obj: Classes.IfStatement):
        self.do_else = True
        if obj.condition.accept(self):
            obj.statements.accept(self)
            self.do_else = False
        if self.do_else:
            for elif_stmt in obj.elif_stmts:
                elif_stmt.accept(self)
                if self.return_flag:
                    break
        if self.do_else and obj.else_stmt:
            obj.else_stmt.accept(self)

    def visit_elif_block(self, obj: Classes.ElifBlock):
        if obj.condition.accept(self):
            obj.statements.accept(self)
            self.do_else = False

    def visit_else_block(self, obj: Classes.ElseBlock):
        for statement in obj:
            statement.accept(self)
            if self.return_flag:
                break

    def visit_for_statement(self, obj: Classes.ForStatement):
        self._add_context()
        self.evaluate = False
        iterator = obj.iterator.accept(self)
        self.evaluate = True
        iterable = obj.iterable.accept(self)
        try:
            for i in iterable.value:
                self._set_local_var(iterator, i)
                obj.statements.accept(self)
                if self.return_flag:
                    break
        except TypeError:
            self.error_handler.handle_error(NotIterableException(type_name=type(iterable.value)))
        self._drop_context()

    def visit_while_statement(self, obj: Classes.WhileStatement):
        self._add_context()
        while obj.condition.accept(self):
            obj.statements.accept(self)
            if self.return_flag:
                break
        self._drop_context()

    def visit_basic_assignment(self, obj: Classes.BasicAssignment):
        if not self._is_assignable(obj.left_expr):
            self.error_handler.handle_error(CannotAssignException(value=obj.left_expr))
        self.evaluate = False
        left = obj.left_expr.accept(self)
        self.evaluate = True
        right = obj.right_expr.accept(self)
        self._set_local_var(left, right)

    def visit_modifying_assignment(self, obj: Classes.Assignment):
        left = obj.left_expr.accept(self)
        right = obj.right_expr.accept(self)
        try:
            _locals = locals()
            exec(f"left{obj.operator}right", globals(), _locals)
            left = _locals["left"]
        except TypeError:
            self.error_handler.handle_error(
                UnsupportedOperandException(operator=obj.operator, l_type=type(left), r_type=type(right)))
        except NameError:
            self.error_handler.handle_error(NotDefinedException(name=left))
        self._set_local_var(left.name, left)

    def visit_two_sided_expression(self, obj: Classes.TwoSidedExpression):
        left = obj.left_expr.accept(self)
        right = obj.right_expr.accept(self)
        result = None
        try:
            result = eval(f"left {obj.operator} right")
            if type(result) == Variable:
                result = result.value
            if type(result) != Value:
                result = Value(result)
        except TypeError:
            self.error_handler.handle_error(
                UnsupportedOperandException(operator=obj.operator, l_type=type(left.value), r_type=type(right.value)))
        return result

    def visit_return_statement(self, obj: Classes.ReturnStatement):
        self.return_flag = True
        self.last_returned = [el.accept(self) for el in obj.values]
        if len(self.last_returned) == 0:
            self.last_returned = Value(None)
        elif len(self.last_returned) == 1:
            self.last_returned = self.last_returned[0]

    def visit_invert_expression(self, obj: Classes.InvertExpr):
        value = obj.value.accept(self)
        result = None
        try:
            result = -value
        except TypeError:
            self.error_handler.handle_error(BadOperandForUnaryException(type_name=type(obj.value)))
        return result

    def visit_dot_operator(self, obj: Classes.DotOperator):
        self.evaluate = True
        left = obj.left_expr.accept(self)
        self.evaluate = False
        right = obj.right_expr.accept(self)
        self.evaluate = True
        result = None
        try:
            if type(left) in [Variable, Value]:
                result = eval(f"left.value.{right}")
            else:
                result = eval(f"left.{right}")
        except AttributeError:
            self.error_handler.handle_error(AttributeException(type_name=type(left.value), value=right))
        return result

    def _run_local_function(self, function_name, arguments):
        function = self.program.functions[function_name]
        if len(arguments) != len(function.params):
            self.error_handler.handle_error(
                MismatchedArgsCountException(fun_name=function_name, expected_number=len(function.params),
                                             got_number=len(arguments)))
        self.evaluate = False
        self._add_function_context()
        self._add_context()
        for arg, param in zip(arguments, function.params):
            self._set_local_var(param.accept(self), arg)
        self.evaluate = True
        function.accept(self)
        self._drop_context()
        self._drop_function_context()
        result = self.last_returned
        return result

    def _run_builtin_function(self, function_name, arguments):
        result = None
        function = function_name
        if not callable(function):
            try:
                function = eval(f"{function_name}")
            except NameError:
                self.error_handler.handle_error(NotDefinedException(name=function_name))
        try:
            result = Value(function(*[arg.value for arg in arguments]))
        except TypeError:
            self.error_handler.handle_error(MismatchedArgsCountException(fun_name=function_name))
        except Exception as e:
            self.error_handler.handle_error(UnknownException(e))
        return result

    def visit_fun_call(self, obj: Classes.FunCall):
        self.evaluate = False
        function_name = obj.left_expr.accept(self)
        self.evaluate = True
        arguments = []
        for arg in obj.right_expr:
            arguments.append(arg.accept(self))
        if function_name in self.program.functions.keys():
            result = self._run_local_function(function_name, arguments)
        else:
            result = self._run_builtin_function(function_name, arguments)
        return result

    def visit_list_element(self, obj: Classes.ListElement):
        list_name = obj.left_expr.accept(self)
        index = obj.right_expr.accept(self)
        result = None
        try:
            if type(list_name) in [Variable, Value]:
                result = eval(f"list_name.value[{index.value}]")
            else:
                result = eval(f"list_name[{index.value}]")
        except IndexError:
            self.error_handler.handle_error(OutOfRangeException())
        return result


if __name__ == '__main__':
    error_handler = ErrorHandler()
    with open("../../Examples/test.tut", "r") as file:
        try:
            lexer = Lexer(file, error_handler)
        except LexerException as e:
            exit(-1)
        parser = Parser(error_handler)
        try:
            program = parser.parse(lexer)
        except ParserException as e:
            exit(-2)

    interpreter = Interpreter(error_handler)
    try:
        interpreter.execute(program, "main")
    except InterpreterException as e:
        exit(-3)
