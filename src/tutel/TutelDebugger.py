import signal

from tutel import Tutel, TutelOptions
from tutel.ErrorHandlerModule.ErrorType import InterpreterException
from tutel.InterpreterModule.Interpreter import Interpreter
from tutel.InterpreterModule.StackFrame import StackFrame

commands = {}


class Restart(Exception):
    pass


class Stop(Exception):
    pass


class Exit(Exception):
    pass


class TutelDebugger(Tutel):
    def command(*cmds):
        def wrapper(func):
            for cmd in cmds:
                commands.update(**{cmd: func.__name__})

            def inner(self, *args, **kwargs):
                return func(self, *args, **kwargs)

            return inner

        return wrapper

    def __init__(self, code: str, options: TutelOptions = TutelOptions()):
        super().__init__(code, options)
        self.breakpoints = set()
        self.cmd = self.do_nothing
        self.cmd_args = []
        self.interpreter = Interpreter(debugger=self)
        self.bp_possible_lines = self._get_bp_possible_lines()
        self.step_mode = False
        self.next_mode = False
        self.watched_frame = None
        self.running = False

    def start(self):
        try:
            signal.signal(signal.SIGINT, self.do_exit)
            while True:
                self._do_command()
        except Exit:
            pass

    def _clean_up(self):
        # self.breakpoints = set()
        self.cmd = self.do_nothing
        self.cmd_args = []
        self.step_mode = False
        self.next_mode = False
        self.watched_frame = None
        self.running = False
        self.interpreter.clean_up()

    def _get_bp_possible_lines(self):
        result = set()

        lines = str.splitlines(self.code)
        for i in range(len(lines)):
            if not lines[i].split("#")[0].isspace():
                result.add(i + 1)

        return result

    def get_cmd(self):
        cmd = cmd_args = None
        while (cmd_function_name := commands.get(cmd)) is None:
            cmd_and_args = input("> ")
            cmd = cmd_and_args.split(" ")[0]
            cmd_args = cmd_and_args.split(" ")[1:]
        self.cmd = getattr(self, cmd_function_name)
        self.cmd_args = cmd_args

    def _do_command(self):
        self.cmd = self.do_nothing
        while self.cmd not in [self.do_continue, self.do_step, self.do_next]:
            self.get_cmd()
            self.cmd(*self.cmd_args)

    def run(self):
        try:
            self.interpreter.execute(self.program, "main")
        except InterpreterException:
            self.post_morten()

    def on_line_change(self, lineno: int, frame: StackFrame):
        if self.step_mode or (self.next_mode and frame.index == self.watched_frame) or lineno in self.breakpoints:
            self.stack_trace()

    def on_frame_drop(self, frame: StackFrame):
        if self.next_mode and frame.index == self.watched_frame:
            self.stack_trace()

    def stack_trace(self):
        print(f"Program stopped in function {self.interpreter.curr_frame.name} "
              f"at line {self.interpreter.curr_frame.lineno}")
        self._do_command()

    def post_morten(self):
        print("Program raised exception. Entering post mortem mode.")
        self.running = False
        self._do_command()

    def set_breakpoint(self, line: int):
        if line not in self.bp_possible_lines:
            print(f"Count not set breakpoint at line {line})")
            return
        if line not in self.breakpoints:
            print(f"Breakpoint set at line {line}")
            self.breakpoints.add(line)

    def remove_breakpoint(self, line: int):
        try:
            self.breakpoints.remove(line)
            print(f"Breakpoint removed from line {line}")
        except KeyError:
            print(f"There is no breakpoint at line {line}")

    @command()
    def do_nothing(self, *args):
        pass

    @command("r", "run")
    def do_run(self, *args):
        stop = False
        while not stop:
            if not self.running:
                self.running = True
                try:
                    self.run()
                except Restart:
                    pass
                except Stop:
                    stop = True
                else:
                    self.running = False
                    stop = True
                finally:
                    self._clean_up()
            else:
                print("Program is already running, use command `restart` to restart it")
                return

    @command("restart")
    def do_restart(self, *args):
        if self.running:
            raise Restart
        else:
            print("Program is not running, use command `r(un)` to run it")

    @command("stop")
    def do_stop(self, *args):
        if self.running:
            print("Stopping program. Debugger is still running, use command `exit` to stop it")
            raise Stop
        else:
            print("Program is not running, use command `r(un)` to run it")

    @command("exit")
    def do_exit(self, *args):
        print("Exiting debugger")
        raise Exit

    @command("c", "continue")
    def do_continue(self, *args):
        self.step_mode = False
        self.next_mode = False
        self.watched_frame = None

    @command("s", "step")
    def do_step(self, *args):
        self.next_mode = False
        self.step_mode = True
        if not self.running:
            self.do_run()

    @command("n", "next")
    def do_next(self, *args):
        self.step_mode = False
        self.next_mode = True
        if not self.running:
            self.watched_frame = 0
            self.do_run()
        else:
            self.watched_frame = self.interpreter.curr_frame.index

    @command("stack")
    def do_stack(self, *args):
        if len(self.interpreter.call_stack) == 0:
            print("Stack is empty")
            return
        if not args:
            print(self.interpreter.curr_frame)
            return
        try:
            index = int(args[0])
            print(list(reversed(self.interpreter.call_stack))[index])
        except TypeError as e:
            print(f"Argument of `s(tack)` command should be integer, not {type(args[0])}")
        except IndexError:
            print(f"Stack index out of range, stack size is {len(self.interpreter.call_stack)}")

    @command("b", "break")
    def do_break(self, *args):
        if not args:
            if len(self.breakpoints) > 0:
                print(f"Breakpoints are set at lines: {self.breakpoints}")
            else:
                print(f"There are no breakpoints set")
            return
        try:
            for arg in args:
                lineno = int(arg)
                self.set_breakpoint(lineno)

        except TypeError:
            print(f"Arguments of `b(reak)` command should be integers")

    @command("clear")
    def do_clear(self, *args):
        if not args:
            if len(self.breakpoints) > 0:
                self.breakpoints = set()
                print(f"All breakpoints removed")
            else:
                print("There are no breakpoints to remove")
            return
        try:
            for arg in args:
                lineno = int(arg)
                self.remove_breakpoint(lineno)

        except TypeError:
            print(f"Arguments of `clear` command should be integers")
