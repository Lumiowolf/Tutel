import argparse
import atexit
import os
import signal
import sys
import threading
from time import sleep

from Tutel.core.Runner.TutelOptions import TutelOptions
from Tutel.debugger.RequestsHandler.StdRequestsHandler import StdRequestsHandler
from Tutel.debugger.RequestsHandler.WebSocketsRequestsHandler import WebSocketsRequestsHandler
from Tutel.debugger.TutelDebuggerInteractive import TutelDebuggerInteractive


def get_arg_parser():
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument(
        "-f",
        "--filename",
        default=None,
        type=argparse.FileType('r'),
        help="Relative or absolute path to a script",
    )

    arg_parser.add_argument(
        "--vscode",
        default=False,
        action="store_true",
    )
    arg_parser.add_argument(
        "--port",
        type=int,
        required=False,
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

    options = {}

    if args.vscode:
        options["gui"] = "vscode"

    if args.output:
        options["gui_out_path"] = args.output

    options = TutelOptions(**options)

    if args.filename:
        args.filename = os.path.realpath(args.filename.name)
    if args.port:
        # Init class
        WebSocketsRequestsHandler.port = args.port

        communication_cls = WebSocketsRequestsHandler
    else:
        communication_cls = StdRequestsHandler
    debugger = TutelDebuggerInteractive(communication_class=communication_cls, filename=args.filename, options=options)
    debugger_thread = threading.Thread(target=debugger.start)
    debugger_thread.start()
    while debugger_thread.is_alive():
        debugger_thread.join(0.5)


def _exit(*args):
    if _exit.alreadyExited:
        return
    _exit.alreadyExited = True
    print("Exiting debugger.")
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
