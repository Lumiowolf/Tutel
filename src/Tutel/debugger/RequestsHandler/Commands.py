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
    STEP = auto()
    NEXT = auto()
    STACK = auto()
    FRAME = auto()
    BREAK = auto()
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
    "s": Command.STEP,
    "step": Command.STEP,
    "n": Command.NEXT,
    "next": Command.NEXT,
    "stack": Command.STACK,
    "frame": Command.FRAME,
    "b": Command.BREAK,
    "break": Command.BREAK,
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
    Command.STEP,
    Command.NEXT,
    Command.STACK,
]

ZERO_OR_ONE_ARG_COMMANDS = [
    Command.BREAK,
    Command.CLEAR,
]

ONE_ARG_COMMANDS = [
    Command.FILE,
    Command.FRAME,
]
