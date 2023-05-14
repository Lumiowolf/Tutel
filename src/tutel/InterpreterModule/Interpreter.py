import operator
from typing import Callable

from tutel.ErrorHandlerModule.ErrorHandler import ErrorHandler
from tutel.ErrorHandlerModule.ErrorType import MismatchedArgsCountException, OutOfRangeException, NothingToRunException, \
    RecursionException, \
    BuiltinFunctionShadowException, TypeException, Exit
from tutel.ErrorHandlerModule.ErrorType import NotIterableException, CannotAssignException, NotDefinedException, \
    UnsupportedOperandException, BadOperandForUnaryException, AttributeException
from tutel.InterpreterModule import TutelBuiltins
from tutel.InterpreterModule.Stack import Stack
from tutel.InterpreterModule.StackFrame import StackFrame
from tutel.InterpreterModule.Turtle.Turtle import Turtle
from tutel.InterpreterModule.TutelDebuggerInterface import TutelDebuggerInterface
from tutel.InterpreterModule.Value import Value
from tutel.ParserModule import Classes


def frame(func):
    def wrapper(self, *args, **kwargs):
        self._add_stack_frame(args[0].name.accept(self), args[0].name.lineno)
        result = func(self, *args, **kwargs)
        self._drop_stack_frame()
        return result

    return wrapper


def update_lineno(func):
    def wrapper(self, *args, **kwargs):
        self.lineno = args[0].lineno
        result = func(self, *args, **kwargs)
        return result

    return wrapper


class Interpreter:
    def __init__(self, error_handler_: ErrorHandler = None, debug=False,
                 debugger: TutelDebuggerInterface = None) -> None:
        self.call_stack = Stack()
        self.dropped_frame = None
        self.running = False
        self.stopped = False
        self.debug = debug
        self.program_to_execute = None
        self.start_with_fun = None
        self.builtins = TutelBuiltins
        self.program_globals: dict[str, any] = {}
        self.return_flag = False
        self.last_returned = None
        self.do_else = True
        self.function_args = None
        self.__lineno = -1

        self.error_handler = error_handler_
        if self.error_handler is None:
            self.error_handler = ErrorHandler(module="interpreter")

        self.debugger = debugger
        if self.debug and not self.debugger:
            self.debugger = TutelDebuggerInterface()

    def clean_up(self):
        self.call_stack = Stack()
        self.dropped_frame = None
        self.running = False
        self.stopped = False
        self.program_to_execute = None
        self.start_with_fun = None
        self.builtins = TutelBuiltins
        self.program_globals: dict[str, any] = {}
        self.return_flag = False
        self.last_returned = None
        self.do_else = True
        self.function_args = None
        self.__lineno = -1
        Turtle.id = Turtle.default_id

    @property
    def curr_frame(self) -> StackFrame:
        return self.call_stack[-1]

    @property
    def lineno(self) -> int:
        return self.__lineno

    @lineno.setter
    def lineno(self, lineno: int):
        if lineno != self.lineno:
            self.curr_frame.lineno = lineno
            self.__lineno = lineno
            # self.debugger.check_line()
            if self.debugger:
                self.debugger.on_line_change(lineno, self.curr_frame)

    # def set_lineno(self, lineno: int):
    #     if lineno != self.lineno:
    #         self.curr_frame.lineno = lineno
    #         self.lineno = lineno
    #         if self.debugger:
    #             self.debugger.on_line_change(lineno, self.curr_frame)

    def execute(self, program_to_execute: Classes.Program, start_with_fun_name: str = None):
        self.clean_up()
        self.program_to_execute = program_to_execute
        self.__lineno = program_to_execute.lineno
        if len(self.program_to_execute.functions) == 0:
            self.error_handler.handle_error(NothingToRunException(), self.call_stack)
        self._add_functions_to_globals(self.program_to_execute)
        if start_with_fun_name in self.program_to_execute.functions.keys():
            self.start_with_fun = start_with_fun_name
        elif start_with_fun_name is None:
            self.start_with_fun = list(self.program_to_execute.functions.keys())[0]
        else:
            self.error_handler.handle_error(NotDefinedException(name=start_with_fun_name), self.call_stack)
        try:
            self.program_globals[self.start_with_fun].accept(self)
        except RecursionError:
            self.error_handler.handle_error(RecursionException(), self.call_stack)

    def _add_stack_frame(self, fname: str = None, lineno: int = None):
        self.call_stack.append(StackFrame(fname, lineno))

    def _drop_stack_frame(self):
        self.dropped_frame = self.call_stack.pop()
        # self.debugger.check_line()
        if self.debugger:
            self.stopped = True
            while self.stopped:
                pass
        self.dropped_frame = None

    def _add_functions_to_globals(self, program_: Classes.Program):
        for fun_name in program_.functions:
            if fun_name in self.program_globals:
                self.error_handler.handle_error(
                    BuiltinFunctionShadowException(fun_name=fun_name), self.call_stack
                )
            else:
                self.program_globals[fun_name] = program_.functions[fun_name]

    def _set_local_var(self, name: str, value: Value):
        if name in self.program_globals:
            self.error_handler.handle_error(
                BuiltinFunctionShadowException(fun_name=name), self.call_stack
            )
        else:
            self.curr_frame.locals[name] = value

    def _get_local_var(self, var_name: str) -> Value | None:
        return self.curr_frame.locals.get(var_name)

    def _get_builtin_global_or_local_var(self, name: str) -> Callable | Classes.Function | Value | None:
        try:
            return getattr(self.builtins, name)
        except AttributeError:
            pass
        return self.program_globals.get(name) or self._get_local_var(name)

    def _get_variable_or_instant_value(self, obj) -> Value | Callable | Classes.Function | None:
        if type(obj) == Classes.Identifier:
            identifier = obj.accept(self)
            if (value := self._get_builtin_global_or_local_var(identifier)) is None:
                self.error_handler.handle_error(NotDefinedException(name=identifier), self.call_stack)
        else:
            value = obj.accept(self)
        return value

    @staticmethod
    def _is_assignable(obj):
        return issubclass(type(obj), Classes.Assignable)

    def execute(self, program_to_execute: Classes.Program, start_with_fun_name: str = None):
        self.clean_up()
        self.running = True
        self.program_to_execute = program_to_execute
        self.__lineno = program_to_execute.lineno
        if len(self.program_to_execute.functions) == 0:
            self.error_handler.handle_error(NothingToRunException(), self.call_stack)
        self._add_functions_to_globals(self.program_to_execute)
        if start_with_fun_name in self.program_to_execute.functions.keys():
            self.start_with_fun = start_with_fun_name
        elif start_with_fun_name is None:
            self.start_with_fun = list(self.program_to_execute.functions.keys())[0]
        else:
            self.error_handler.handle_error(NotDefinedException(name=start_with_fun_name), self.call_stack)
        try:
            self.program_globals[self.start_with_fun].accept(self)
        except RecursionError:
            self.error_handler.handle_error(RecursionException(), self.call_stack)
        self.running = False

    def visit_program(self, _):
        self.start_with_fun.accept(self)

    @frame
    @update_lineno
    def visit_function(self, function: Classes.Function):
        if self.function_args is not None:
            if len(self.function_args) != len(function.params):
                self.error_handler.handle_error(
                    MismatchedArgsCountException(
                        fun_name=function.name,
                        expected_min=len(function.params),
                        expected_max=len(function.params),
                        got_number=len(self.function_args)
                    ), self.call_stack
                )
            for arg, param in zip(self.function_args, function.params):
                self._set_local_var(param.accept(self), arg)

        function.statements.accept(self)
        self.return_flag = False

        self.function_args = None

    @update_lineno
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
        return Value([self._get_variable_or_instant_value(el) for el in list_.value])

    @update_lineno
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

    @update_lineno
    def visit_elif_block(self, elif_block: Classes.ElifBlock):
        if elif_block.condition.accept(self):
            elif_block.statements.accept(self)
            self.do_else = False

    @update_lineno
    def visit_else_block(self, else_block: Classes.ElseBlock):
        for statement in else_block:
            statement.accept(self)
            if self.return_flag:
                break

    @update_lineno
    def visit_for_statement(self, for_stmt: Classes.ForStatement):
        iterator = for_stmt.iterator.accept(self)
        iterable = self._get_variable_or_instant_value(for_stmt.iterable)
        try:
            for i in iterable:
                self._set_local_var(iterator, i)
                for_stmt.statements.accept(self)
                if self.return_flag:
                    break
        except TypeError:
            self.error_handler.handle_error(NotIterableException(type_name=type(iterable.value).__name__),
                                            self.call_stack)

    @update_lineno
    def visit_while_statement(self, while_stmt: Classes.WhileStatement):
        while while_stmt.condition.accept(self):
            while_stmt.statements.accept(self)
            if self.return_flag:
                break

    @update_lineno
    def visit_return_statement(self, return_stmt: Classes.ReturnStatement):
        self.return_flag = True
        self.last_returned = [el.accept(self) for el in return_stmt.values]
        if len(self.last_returned) == 0:
            self.last_returned = Value(None)
        elif len(self.last_returned) == 1:
            self.last_returned = self.last_returned[0]

    @update_lineno
    def visit_basic_assignment(self, assignment: Classes.BasicAssignment):
        if not self._is_assignable(assignment.left_expr):
            self.error_handler.handle_error(CannotAssignException(value=assignment.left_expr), self.call_stack)
        identifier = assignment.left_expr.accept(self)
        value = self._get_variable_or_instant_value(assignment.right_expr)
        if type(value) != Value:
            value = Value(value)
        self._set_local_var(identifier, value)

    @update_lineno
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
            self.error_handler.handle_error(NotDefinedException(name=identifier), self.call_stack)
        else:
            value = self._get_variable_or_instant_value(assignment.right_expr)
            if type(value) != Value:
                value = Value(value)
            try:
                operators[assignment.operator](variable, value)
            except TypeError as e:
                self.error_handler.handle_error(
                    UnsupportedOperandException(l_type=type(variable).__name__, r_type=type(value).__name__,
                                                operator=assignment.operator), self.call_stack
                )

    @update_lineno
    def visit_one_sided_expression(self, expr: Classes.OneSidedExpression):
        operators = {
            "-": operator.neg,
            "not": operator.not_,
        }
        value = self._get_variable_or_instant_value(expr.value)
        result = None
        try:
            result = operators[expr.operator](value)
        except TypeError:
            self.error_handler.handle_error(
                BadOperandForUnaryException(type_name=type(value).__name__), self.call_stack)
        return result

    @update_lineno
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
        left = self._get_variable_or_instant_value(expr.left_expr)
        right = self._get_variable_or_instant_value(expr.right_expr)
        result = None
        try:
            result = operators[expr.operator](left, right)
        except (KeyError, TypeError) as e:
            self.error_handler.handle_error(
                UnsupportedOperandException(operator=expr.operator, l_type=type(left).__name__,
                                            r_type=type(right).__name__), self.call_stack)
        return result

    @update_lineno
    def visit_dot_operator(self, obj: Classes.DotOperator):
        left = self._get_variable_or_instant_value(obj.left_expr)
        right = obj.right_expr.accept(self)
        result = None
        try:
            result = getattr(left, right)
        except AttributeError:
            self.error_handler.handle_error(AttributeException(type_name=type(left.value).__name__, value=right),
                                            self.call_stack)
        return result

    @update_lineno
    def visit_fun_call(self, fun_call: Classes.FunCall):
        function = self._get_variable_or_instant_value(fun_call.left_expr)
        arguments = []
        for arg in fun_call.right_expr:
            arguments.append(self._get_variable_or_instant_value(arg))
        if type(function) == Classes.Function:
            try:
                self.function_args = arguments
                function.accept(self)
                result = self.last_returned
                return result
            except TypeError as err:
                self.error_handler.handle_error(TypeException(err), self.call_stack)
        else:
            try:
                result = function(*[arg.value for arg in arguments])
                if type(result) != Value:
                    result = Value(result)
                return result
            except TypeError as e:
                self.error_handler.handle_error(
                    TypeException(e), self.call_stack
                )

    @update_lineno
    def visit_list_element(self, list_el: Classes.ListElement):
        list_ = self._get_variable_or_instant_value(list_el.left_expr)
        index = self._get_variable_or_instant_value(list_el.right_expr)
        result = None
        try:
            result = list_[index.value]
        except IndexError:
            self.error_handler.handle_error(OutOfRangeException(), self.call_stack)
        return result
