import Tutel.core as tutel
from Tutel.core.InterpreterModule.Value import Value


class StackFrame(dict):
    index = 0

    def __init__(self, name, lineno):
        super().__init__()
        self.index = StackFrame.index
        StackFrame.index += 1
        self.file = None
        self.name = name
        self.lineno = lineno
        self.locals = {}
        if tutel.VERBOSE:
            print(f"Created frame {self.index}")

    @property
    def file(self) -> str:
        return self["file"]

    @file.setter
    def file(self, f):
        self["file"] = f

    @property
    def name(self) -> str:
        return self["name"]

    @name.setter
    def name(self, n):
        self["name"] = n

    @property
    def lineno(self) -> int:
        return self["lineno"]

    @lineno.setter
    def lineno(self, lno):
        self["lineno"] = lno

    @property
    def locals(self) -> dict[str, Value]:
        return self["locals"]

    @locals.setter
    def locals(self, loc):
        self["locals"] = loc

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
