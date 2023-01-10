class Position:
    def __init__(self, x, y):
        self.__x = x
        self.__y = y

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    def __iter__(self):
        for el in [self.x, self.y]:
            yield el

    def dict(self):
        return {"position": {"x": self.x, "y": self.y}}

    def __repr__(self) -> str:
        return "{" + f'"x": {self.x}, ' \
                     f'"y": {self.y}' + "}"
