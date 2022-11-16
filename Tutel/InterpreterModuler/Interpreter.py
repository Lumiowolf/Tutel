import inspect
import operator
from typing import Callable

from Tutel.ErrorHandlerModule.ErrorHandler import ErrorHandler
from Tutel.ErrorHandlerModule.ErrorType import LexerException, ParserException, InterpreterException, \
    MismatchedArgsCountException, OutOfRangeException, UnknownException, NothingToRunException, RecursionException, \
    BuiltinFunctionShadowException, TypeException
from Tutel.ErrorHandlerModule.ErrorType import NotIterableException, CannotAssignException, NotDefinedException, \
    UnsupportedOperandException, BadOperandForUnaryException, AttributeException
from Tutel.InterpreterModuler.TutelBuiltins import GLOBAL_FUNCTIONS
from Tutel.InterpreterModuler.Value import Value
from Tutel.LexerModule.Lexer import Lexer
from Tutel.ParserModule import Classes
from Tutel.ParserModule.Parser import Parser


class Interpreter:
    def __init__(self, error_handler_: ErrorHandler) -> None:
        self.is_running = False
        self.error_handler = error_handler_
        self.program_to_execute = None
        self.start_with_fun = None
        self.program_context: list[list[dict[str, Value]]] = []
        self.program_globals: dict[str, any] = {}
        self._prepare_globals()
        self.return_flag = False
        self.last_returned = None
        self.do_else = True
        self.call_stack = []
        self.function_args = None

    def execute(self, program_to_execute: Classes.Program, start_with_fun_name: str = None):
        self.is_running = True
        self.program_to_execute = program_to_execute
        if len(self.program_to_execute.functions) == 0:
            self.error_handler.handle_error(NothingToRunException())
        self._add_functions_to_globals(self.program_to_execute)
        if start_with_fun_name in self.program_to_execute.functions.keys():
            self.start_with_fun = start_with_fun_name
        elif start_with_fun_name is None:
            self.start_with_fun = list(self.program_to_execute.functions.keys())[0]
        else:
            self.error_handler.handle_error(NotDefinedException(name=start_with_fun_name))
        try:
            self.program_globals[self.start_with_fun].accept(self)
        except RecursionError:
            self.error_handler.handle_error(RecursionException())

    def stop(self):
        self.is_running = False

    def _add_function_context(self):
        self.program_context.append([])

    def _add_context(self):
        self.program_context[-1].append({})

    def _drop_context(self):
        self.program_context[-1] = self.program_context[-1][:-1]

    def _drop_function_context(self):
        self.program_context = self.program_context[:-1]

    def _prepare_globals(self):
        self.program_globals.update(**GLOBAL_FUNCTIONS)

    def _add_functions_to_globals(self, program_: Classes.Program):
        for fun_name in program_.functions:
            if fun_name in self.program_globals:
                self.error_handler.handle_error(
                    BuiltinFunctionShadowException(fun_name=fun_name)
                )
            else:
                self.program_globals[fun_name] = program_.functions[fun_name]

    def _set_local_var(self, name: str, value: Value):
        if name in self.program_globals:
            self.error_handler.handle_error(
                BuiltinFunctionShadowException(fun_name=name)
            )
        else:
            self.program_context[-1][-1][name] = value

    def _get_local_var(self, var_name: str) -> Value | None:
        for i in range(len(self.program_context[-1]) - 1, -1, -1):
            if (val := self.program_context[-1][i].get(var_name)) is not None:
                return val
        if (val := self.program_globals.get(var_name)) is not None:
            return val
        return None

    def _get_value_or_variable(self, obj) -> Value | Callable | Classes.Function | None:
        if type(obj) == Classes.Identifier:
            identifier = obj.accept(self)
            if (value := self._get_local_var(identifier)) is None:
                self.error_handler.handle_error(NotDefinedException(name=identifier))
        else:
            value = obj.accept(self)
        return value

    @staticmethod
    def _is_assignable(obj):
        return issubclass(type(obj), Classes.Assignable)

    def visit_program(self, _):
        self.start_with_fun.accept(self)

    def visit_function(self, function: Classes.Function):
        self._add_function_context()
        self._add_context()

        if self.function_args is not None:
            if len(self.function_args) != len(function.params):
                self.error_handler.handle_error(
                    MismatchedArgsCountException(
                        fun_name=function.name,
                        expected_min=len(function.params),
                        expected_max=len(function.params),
                        got_number=len(self.function_args)
                    )
                )
            for arg, param in zip(self.function_args, function.params):
                self._set_local_var(param.accept(self), arg)

        function.statements.accept(self)
        self.return_flag = False

        self.function_args = None

        self._drop_context()
        self._drop_function_context()

    def visit_block(self, block: Classes.Block):
        for statement in block:
            statement.accept(self)
            if self.return_flag:
                break

    @staticmethod
    def visit_atom(atom: Classes.Atom):
        return Value(atom.value)

    @staticmethod
    def visit_identifier(identifier: Classes.Identifier):
        return identifier.value

    def visit_list(self, list_: Classes.List):
        return Value([el.accept(self) for el in list_.value])

    def visit_if_statement(self, if_stmt: Classes.IfStatement):
        self.do_else = True
        if if_stmt.condition.accept(self):
            if_stmt.statements.accept(self)
            self.do_else = False
        if self.do_else:
            for elif_stmt in if_stmt.elif_stmts:
                elif_stmt.accept(self)
                if self.return_flag:
                    break
        if self.do_else and if_stmt.else_stmt:
            if_stmt.else_stmt.accept(self)

    def visit_elif_block(self, elif_block: Classes.ElifBlock):
        if elif_block.condition.accept(self):
            elif_block.statements.accept(self)
            self.do_else = False

    def visit_else_block(self, else_block: Classes.ElseBlock):
        for statement in else_block:
            statement.accept(self)
            if self.return_flag:
                break

    def visit_for_statement(self, for_stmt: Classes.ForStatement):
        self._add_context()
        iterator = for_stmt.iterator.accept(self)
        iterable = self._get_value_or_variable(for_stmt.iterable)
        try:
            for i in iterable:
                self._set_local_var(iterator, i)
                for_stmt.statements.accept(self)
                if self.return_flag:
                    break
        except TypeError:
            self.error_handler.handle_error(NotIterableException(type_name=type(iterable.value)))
        self._drop_context()

    def visit_while_statement(self, while_stmt: Classes.WhileStatement):
        self._add_context()
        while while_stmt.condition.accept(self):
            while_stmt.statements.accept(self)
            if self.return_flag:
                break
        self._drop_context()

    def visit_return_statement(self, obj: Classes.ReturnStatement):
        self.return_flag = True
        self.last_returned = [el.accept(self) for el in obj.values]
        if len(self.last_returned) == 0:
            self.last_returned = Value(None)
        elif len(self.last_returned) == 1:
            self.last_returned = self.last_returned[0]

    def visit_basic_assignment(self, assignment: Classes.BasicAssignment):
        if not self._is_assignable(assignment.left_expr):
            self.error_handler.handle_error(CannotAssignException(value=assignment.left_expr))
        identifier = assignment.left_expr.accept(self)
        value = self._get_value_or_variable(assignment.right_expr)
        if type(value) != Value:
            value = Value(value)
        self._set_local_var(identifier, value)

    def visit_modifying_assignment(self, assignment: Classes.ModifyingAssignment):
        operators = {
            "+=": lambda a, b: a.__iadd__(b),
            "-=": lambda a, b: a.__isub__(b),
            "*=": lambda a, b: a.__imul__(b),
            "/=": lambda a, b: a.__idiv__(b),
            "%=": lambda a, b: a.__imod__(b),
        }
        identifier = assignment.left_expr.accept(self)
        if (variable := self._get_local_var(identifier)) is None:
            self.error_handler.handle_error(NotDefinedException(name=identifier))
        else:
            value = self._get_value_or_variable(assignment.right_expr)
            if type(value) != Value:
                value = Value(value)
            try:
                operators[assignment.operator](variable, value)
            except TypeError:
                self.error_handler.handle_error(
                    UnsupportedOperandException(l_type=type(variable).__name__, r_type=type(value).__name__,
                                                operator=assignment.operator)
                )

    def visit_one_sided_expression(self, expr: Classes.OneSidedExpression):
        operators = {
            "-": operator.neg,
            "not": operator.not_,
        }
        value = self._get_value_or_variable(expr.value)
        result = None
        try:
            result = operators[expr.operator](value)
        except TypeError:
            self.error_handler.handle_error(
                BadOperandForUnaryException(type_name=type(value)))
        return result

    def visit_two_sided_expression(self, expr: Classes.TwoSidedExpression):
        operators = {
            "==": operator.eq,
            "!=": operator.ne,
            "<": operator.lt,
            "<=": operator.le,
            ">": operator.gt,
            ">=": operator.ge,
            "and": lambda a, b: a and b,
            "or": lambda a, b: a or b,
            "in": lambda a, b: a in b,
            "+": operator.add,
            "-": operator.sub,
            "*": operator.mul,
            "/": operator.truediv,
            "//": operator.floordiv,
            "%": operator.mod,
        }
        left = self._get_value_or_variable(expr.left_expr)
        right = self._get_value_or_variable(expr.right_expr)
        result = None
        try:
            result = operators[expr.operator](left, right)
        except (KeyError, TypeError):
            self.error_handler.handle_error(
                UnsupportedOperandException(operator=expr.operator, l_type=type(left).__name__,
                                            r_type=type(right).__name__))
        return result

    def visit_dot_operator(self, obj: Classes.DotOperator):
        left = self._get_value_or_variable(obj.left_expr)
        right = obj.right_expr.accept(self)
        result = None
        try:
            result = getattr(left, right)
        except AttributeError:
            self.error_handler.handle_error(AttributeException(type_name=type(left.value).__name__, value=right))
        return result

    def visit_fun_call(self, fun_call: Classes.FunCall):
        function = self._get_value_or_variable(fun_call.left_expr)
        arguments = []
        for arg in fun_call.right_expr:
            arguments.append(self._get_value_or_variable(arg))
        if type(function) == Classes.Function:
            try:
                self.function_args = arguments
                function.accept(self)
                result = self.last_returned
                return result
            except TypeError as err:
                self.error_handler.handle_error(TypeException(err))
        else:
            try:
                return Value(function(*[arg.value for arg in arguments]))
            except TypeError:
                args_spec = inspect.getfullargspec(function)
                self.error_handler.handle_error(
                    MismatchedArgsCountException(
                        fun_name=function.__name__,
                        got_number=len(arguments),
                        expected_min=len(args_spec.args) - len(args_spec.defaults if args_spec.defaults else []),
                        expected_max=len(args_spec.args)
                    )
                )
            except Exception as err:
                self.error_handler.handle_error(UnknownException(err))

    def visit_list_element(self, list_el: Classes.ListElement):
        list_ = self._get_value_or_variable(list_el.left_expr)
        index = self._get_value_or_variable(list_el.right_expr)
        result = None
        try:
            result = list_[index.value]
        except IndexError:
            self.error_handler.handle_error(OutOfRangeException())
        return result


if __name__ == '__main__':
    error_handler = ErrorHandler()
    with open("../../Examples/example_5.tut", "r") as file:
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
    from Tutel.InterpreterModuler.Turtle.Turtle import Turtle
    from Tutel.GuiModule.GuiMock import GuiMock

    Turtle.set_gui(GuiMock())
    try:
        interpreter.execute(program, "main")
    except InterpreterException as e:
        exit(-3)
