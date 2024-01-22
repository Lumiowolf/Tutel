from enum import Enum, auto


class Command(Enum):
    HELP = auto()
    FILE = auto()
    BP_LINES = auto()
    UNKNOWN = auto()
    RUN = auto()
    RUN_UNSTOPPABLE = auto()
    RESTART = auto()
    STOP = auto()
    EXIT = auto()
    CONTINUE = auto()
    STEP_INTO = auto()
    STEP_OVER = auto()
    PAUSE = auto()
    STACK = auto()
    FRAME = auto()
    BREAK = auto()
    BREAK_EXPRESSION = auto()
    CLEAR = auto()


TEXT_TO_COMMAND = {
    "h": Command.HELP,
    "help": Command.HELP,
    "f": Command.FILE,
    "file": Command.FILE,
    "r": Command.RUN,
    "run": Command.RUN,
    "run_no_debug": Command.RUN_UNSTOPPABLE,
    "restart": Command.RESTART,
    "stop": Command.STOP,
    "exit": Command.EXIT,
    "c": Command.CONTINUE,
    "continue": Command.CONTINUE,
    "step_into": Command.STEP_INTO,
    "s": Command.STEP_OVER,
    "step_over": Command.STEP_OVER,
    "pause": Command.PAUSE,
    "stack": Command.STACK,
    "frame": Command.FRAME,
    "b": Command.BREAK,
    "break": Command.BREAK,
    "break_expr": Command.BREAK_EXPRESSION,
    "clear": Command.CLEAR,
    "get_bp_lines": Command.BP_LINES,
}

ZERO_ARG_COMMANDS = [
    Command.HELP,
    Command.BP_LINES,
    Command.RUN,
    Command.RUN_UNSTOPPABLE,
    Command.RESTART,
    Command.STOP,
    Command.EXIT,
    Command.CONTINUE,
    Command.STEP_INTO,
    Command.STEP_OVER,
    Command.PAUSE,
    Command.STACK,
]
