import argparse
import atexit
import os
import signal
import sys
from time import sleep

import Tutel
from Tutel.core.Runner.TutelOptions import TutelOptions
from Tutel.core.Runner.TutelRunner import TutelRunner


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
        "-V",
        "--version",
        default=False,
        action="store_true",
    )
    arg_parser.add_argument(
        "-o",
        "--output",
        required=False
    )

    return arg_parser


def main():
    arg_parser = get_arg_parser()
    args = arg_parser.parse_args()
    if args.version:
        print(f"Tutel {Tutel.__version__}")
        exit(0)

    options = {}

    if args.vscode:
        options["gui"] = "vscode"
    options["verbose"] = args.verbose

    if args.output:
        options["gui_out_path"] = args.output

    options = TutelOptions(**options)

    code = args.code
    if args.filename:
        args.filename = os.path.realpath(args.filename.name)
        with open(args.filename, "r") as file:
            code = file.read()
    if not code:
        print("Nothing to execute")
        exit(0)

    TutelRunner(code=code, options=options).run()


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


