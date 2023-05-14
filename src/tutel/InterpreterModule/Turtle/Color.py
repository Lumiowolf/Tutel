from tutel.InterpreterModule.JsonSerializable import JsonSerializable


class Color(JsonSerializable):
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

    def dict(self):
        return {"color": {"r": self.r, "g": self.g, "b": self.b}}

    def to_json(self):
        return {
            "r": self.r,
            "g": self.g,
            "b": self.b,
        }

    def __repr__(self) -> str:
        return "{" + f'"r": {self.r}, ' \
                     f'"g": {self.g}, ' \
                     f'"b": {self.b}' + "}"
