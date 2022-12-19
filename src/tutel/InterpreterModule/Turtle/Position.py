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

    def __str__(self) -> str:
        return f"(X: {self.x}, Y: {self.y})"

    def dict(self):
        return {"x": self.x, "y": self.y}
