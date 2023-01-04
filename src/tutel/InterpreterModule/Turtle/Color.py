class Color:
    def __init__(self, r, g, b):
        self.__r = r if r in range(0, 256) else 0 if r < 0 else 255
        self.__g = g if g in range(0, 256) else 0 if g < 0 else 255
        self.__b = b if b in range(0, 256) else 0 if b < 0 else 255

    @property
    def r(self):
        return self.__r

    @property
    def g(self):
        return self.__g

    @property
    def b(self):
        return self.__b

    def __iter__(self):
        for el in [self.r, self.g, self.b]:
            yield el

    def __str__(self) -> str:
        return f"(R: {self.r}, G: {self.g}, B: {self.b})"

    def dict(self):
        return {"r": self.r, "g": self.g, "b": self.b}

    def __repr__(self):
        return f"<{self.__class__.__name__} at {hex(id(self))}>"
