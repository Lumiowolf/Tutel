from typing import NamedTuple, Literal


class TutelOptions(NamedTuple):
    gui: Literal["vscode", "nock"] = "mock"
    gui_out_path: str = ""
    verbose: bool = False
