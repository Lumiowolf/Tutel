class Orientation:
    def __init__(self, angle: int):
        self.__angle = angle

    @property
    def angle(self) -> int:
        return self.__angle

    def __str__(self) -> str:
        return f"(angle: {self.angle})"

    def dict(self):
        return {"angle": self.angle}

    def __repr__(self):
        return f"<{self.__class__.__name__} at {hex(id(self))}>"
