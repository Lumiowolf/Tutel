import atexit
import logging
import signal
import sys
import threading
from time import sleep

from Tutel.ErrorHandlerModule.ErrorHandler import ErrorHandler
from Tutel.GuiModule.Gui import Gui
from Tutel.InterpreterModuler.Interpreter import Interpreter


def main():
    error_handler = ErrorHandler(level=logging.CRITICAL)
    gui = Gui(error_handler)
    gui.run()
    gui_thread = threading.Thread(target=gui.run)
    gui_thread.start()
    gui_thread.join()


def _exit(*args):
    if _exit.alreadyExited:
        return
    _exit.alreadyExited = True
    print("Program terminated.")
    atexit._run_exitfuncs()
    for i in range(0, 3):
        sys.stdout.write(".")
        sys.stdout.flush()
        sleep(1)
    print()
    sys.exit(0)


_exit.alreadyExited = False


if __name__ == '__main__':
    signal.signal(signal.SIGINT, _exit)
    main()
