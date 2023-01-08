import tutel
from tutel.InterpreterModule.Value import Value


class StackFrame:
    index = 0

    def __init__(self, name, lineno):
        self.index = StackFrame.index
        StackFrame.index += 1
        self.name = name
        self.lineno = lineno
        self.locals: dict[str, Value] = {}
        if tutel.VERBOSE:
            print(f"Created frame {self.index}")

    def increment_lineno(self):
        if tutel.VERBOSE:
            print(f"Frame {self.index}: {self.lineno} -> {self.lineno + 1}")
        self.lineno += 1

    def __str__(self):
        return f"Function name: {self.name}\nLine number: {self.lineno}\nLocal variables: {self.locals}"

    def __del__(self):
        if tutel.VERBOSE:
            print(f"Deleted frame {self.index}")
        StackFrame.index -= 1
