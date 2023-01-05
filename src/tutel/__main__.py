import argparse
import atexit
import os
import signal
import sys
from time import sleep

import tutel
from tutel import Tutel, TutelOptions
from tutel.TutelDebugger import TutelDebugger


def get_arg_parser():
    arg_parser = argparse.ArgumentParser()

    group = arg_parser.add_mutually_exclusive_group(required=False)

    group.add_argument(
        "-f",
        "--filename",
        default=None,
        type=argparse.FileType('r'),
        help="Relative or absolute path to a script",
    )
    group.add_argument(
        "-c",
        "--code",
        default=None,
        type=str,
        help="Code to execute as a string",
    )

    arg_parser.add_argument(
        "-v",
        "--verbose",
        default=False,
        action="store_true",
    )
    arg_parser.add_argument(
        "--vscode",
        default=False,
        action="store_true",
    )
    arg_parser.add_argument(
        "--version",
        default=False,
        action="store_true",
    )
    arg_parser.add_argument(
        "-d",
        "--debug",
        default=False,
        action="store_true",
    )

    return arg_parser


def main(filename: str | None = None, code: str | None = None, flags: tuple[str] = None):
    if filename and code:
        raise RuntimeError("You should give the filename or the code and not both of them.")
    if filename:
        sys.argv.append("-f")
        sys.argv.append(filename)
    if code:
        sys.argv.append("-c")
        sys.argv.append(code)
    if flags:
        sys.argv += flags
    arg_parser = get_arg_parser()
    args = arg_parser.parse_args()
    if args.version:
        print(f"Tutel {tutel.__version__}")
        exit(0)

    if args.vscode:
        options = TutelOptions(gui="vscode", verbose=args.verbose)
    else:
        options = TutelOptions(verbose=args.verbose)
    if hasattr(args, "filename") and args.filename:
        args.filename = os.path.realpath(args.filename.name)
        with open(filename if filename is not None else args.filename, "r") as file:
            code = file.read()
        if args.debug:
            TutelDebugger(code=code, options=options).start()
        else:
            Tutel(code=code, options=options).run()
    elif hasattr(args, "code") and args.code:
        if args.debug:
            TutelDebugger(code=args.code, options=options).start()
        else:
            Tutel(code=args.code, options=options).run()
    else:
        print("Nothing to execute")
        exit(0)


def _exit(*args):
    if _exit.alreadyExited:
        return
    _exit.alreadyExited = True
    print("Program terminated.")
    atexit._run_exitfuncs()
    for i in range(0, 3):
        sys.stdout.write("")
        sys.stdout.flush()
        sleep(1)
    print()
    sys.exit(0)


_exit.alreadyExited = False

if __name__ == '__main__':
    signal.signal(signal.SIGINT, _exit)
    main()
