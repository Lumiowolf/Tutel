import threading

from tutel.ErrorHandlerModule.ErrorType import InterpreterException, Exit
from tutelDebugger import TutelDebugger

commands = {}


class TutelDebuggerInteractive(TutelDebugger):
    def command(*cmds):
        def wrapper(func):
            for cmd in cmds:
                commands.update(**{cmd: func.__name__})

            def inner(self, *args, **kwargs):
                return func(self, *args, **kwargs)

            return inner

        return wrapper

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.running = False
        self.cmd = self._do_nothing
        self.cmd_args = []
        self.stop = False
        self.exit = False

    def _clean_up(self):
        super()._clean_up()
        self.running = False
        self.cmd = self._do_nothing
        self.cmd_args = []
        self.stop = False
        self.exit = False

    def _get_cmd(self):
        cmd = cmd_args = None
        while (cmd_function_name := commands.get(cmd)) is None:
            cmd_and_args = input("> ")
            cmd = cmd_and_args.split(" ")[0]
            cmd_args = cmd_and_args.split(" ")[1:]
        self.cmd = getattr(self, cmd_function_name)
        self.cmd_args = cmd_args

    def _do_command(self):
        self._get_cmd()
        self.cmd(*self.cmd_args)

    def _stop_session(self):
        self.interpreter.running = False
        self.interpreter.stopped = False

    # def _stack_trace(self):
    #     with self.stdout_mutex:
    #         super()._stack_trace()
    #
    def _post_morten(self, e: InterpreterException):
        super()._post_morten(e)
        self.running = False
        self.stopped = False
        self._stop_session()

    def message(self, msg):
        print(msg)
        print()

    def start(self):
        while not self.exit:
            if (not self.interpreter.running and not self.running) or self.stopped:
                self._do_command()

    def check_line(self):
        if self.step_mode:
            self._stack_trace()
        elif self.next_mode and self.interpreter.curr_frame.index == self.watched_frame:
            self._stack_trace()
        elif self.next_mode and self.interpreter.dropped_frame and self.interpreter.dropped_frame.index == self.watched_frame:
            self._stack_trace()
        elif self.interpreter.lineno in self.breakpoints:
            self._stack_trace()
        else:
            self.interpreter.stopped = False
            self.stopped = False

    @command()
    def _do_nothing(self, *args):
        pass

    @command("r", "run")
    def do_run(self, *args):
        if not self.running:
            self.session = threading.Thread(target=self.run)
            self.session.start()
            self.running = True
        else:
            self.message("Program is already running, use command `restart` to restart it.")

    @command("restart")
    def do_restart(self, *args):
        if self.interpreter.running:
            self._stop_session()
            self.stopped = False
            self.step_mode = False
            self.next_mode = False
            self.message("Restarting program.")
            self.session = threading.Thread(target=self.run)
            self.session.start()
            self.running = True
        else:
            self.message("Program is not running, use command `r(un)` to run it.")

    @command("stop")
    def do_stop(self, *args):
        if self.interpreter.running:
            self._stop_session()
            self.message("Stopping program. Debugger is still running, use command `exit` to stop it.")
        else:
            self.message("Program is not running, use command `r(un)` to run it.")

    @command("exit")
    def do_exit(self, *args):
        self.message("Exiting debugger.")
        self._stop_session()
        self.exit = True

    @command("c", "continue")
    def do_continue(self, *args):
        self.step_mode = False
        self.next_mode = False
        self.watched_frame = None
        if self.interpreter.running:
            self.interpreter.stopped = False
            self.stopped = False
        else:
            self.message("Program is not running, use command `r(un)` to run it.")

    @command("s", "step")
    def do_step(self, *args):
        self.next_mode = False
        self.step_mode = True
        if self.interpreter.running:
            self.interpreter.stopped = False
            self.stopped = False
        else:
            self.do_run()

    @command("n", "next")
    def do_next(self, *args):
        self.step_mode = False
        self.next_mode = True
        if self.interpreter.running:
            self.watched_frame = self.interpreter.curr_frame.index
            self.interpreter.stopped = False
            self.stopped = False
        else:
            self.watched_frame = 0
            self.do_run()

    @command("stack")
    def do_stack(self, *args):
        if len(self.interpreter.call_stack) == 0:
            self.message("Stack is empty.")
            return
        if not args:
            self.message(self.interpreter.call_stack)
            return
        try:
            index = int(args[0])
            self.message(list(reversed(self.interpreter.call_stack))[index])
        except ValueError as e:
            self.message(f"Argument of `s(tack)` command should be integer, not {type(args[0])}.")
        except IndexError:
            self.message(f"Stack index out of range, stack size is {len(self.interpreter.call_stack)}.")

    @command("b", "break")
    def do_break(self, *args):
        if not args:
            if len(self.breakpoints) > 0:
                self.message(f"Breakpoints are set at lines: {self.breakpoints}.")
            else:
                self.message(f"There are no breakpoints set.")
            return
        try:
            for arg in args:
                lineno = int(arg)
                self.set_breakpoint(lineno)

        except TypeError:
            self.message(f"Arguments of `b(reak)` command should be integers.")

    @command("clear")
    def do_clear(self, *args):
        if not args:
            if len(self.breakpoints) > 0:
                self.breakpoints = set()
                self.message(f"All breakpoints removed.")
            else:
                self.message("There are no breakpoints to remove.")
            return
        try:
            for arg in args:
                lineno = int(arg)
                self.remove_breakpoint(lineno)

        except TypeError:
            self.message(f"Arguments of `clear` command should be integers.")
