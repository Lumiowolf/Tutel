class Value:
    values = []

    def __new__(cls, value):
        for val in Value.values:
            if val.value == value and type(val.value) == type(value):
                return val
        obj = object.__new__(cls)
        return obj

    def __init__(self, value):
        self.value = value
        if self not in Value.values:
            Value.values.append(self)

    # def __iter__(self):
    #     return iter(self.value)

    def __neg__(self):
        return Value(-self.value)

    def __add__(self, other):
        return Value(self.value + other.value)

    def __sub__(self, other):
        return Value(self.value - other.value)

    def __mul__(self, other):
        return Value(self.value * other.value)

    def __truediv__(self, other):
        return Value(self.value / other.value)

    def __floordiv__(self, other):
        return Value(self.value // other.value)

    def __mod__(self, other):
        return Value(self.value % other.value)

    # def __iadd__(self, other):
    #     return Value(self.value + other.value)
    #
    # def __isub__(self, other):
    #     return Value(self.value - other.value)
    #
    # def __imul__(self, other):
    #     return Value(self.value * other.value)
    #
    # def __itruediv__(self, other):
    #     return Value(self.value / other.value)
    #
    # def __imod__(self, other):
    #     return Value(self.value % other.value)
    #
    # def __and__(self, other):
    #     return self.value and other.value
    #
    # def __or__(self, other):
    #     return self.value or other.value

    def __contains__(self, item):
        return item in self.value

    def __bool__(self):
        return self.value is True

    def __eq__(self, other):
        return self.value == other.value

    def __ne__(self, other):
        return self.value != other.value

    def __gt__(self, other):
        return self.value > other.value

    def __ge__(self, other):
        return self.value >= other.value

    def __lt__(self, other):
        return self.value < other.value

    def __le__(self, other):
        return self.value <= other.value


class Variable:
    def __init__(self, name: str, value: Value):
        self.name = name
        self.value = value

    @property
    def value(self):
        return self.__value.value

    @value.setter
    def value(self, value):
        if type(value) != Value:
            value = Value(value)
        self.__value = value

    def __neg__(self):
        return Value(-self.value)

    def __add__(self, other):
        return Value(self.value + other.value)

    def __sub__(self, other):
        return Value(self.value - other.value)

    def __mul__(self, other):
        return Value(self.value * other.value)

    def __truediv__(self, other):
        return Value(self.value / other.value)

    def __floordiv__(self, other):
        return Value(self.value // other.value)

    def __mod__(self, other):
        return Value(self.value % other.value)

    def __iadd__(self, other):
        return Variable(self.name, self.value + other.value)

    def __isub__(self, other):
        return Variable(self.name, self.value - other.value)

    def __imul__(self, other):
        return Variable(self.name, self.value * other.value)

    def __itruediv__(self, other):
        return Variable(self.name, self.value / other.value)

    def __imod__(self, other):
        return Variable(self.name, self.value % other.value)

    # def __and__(self, other):
    #     return Value(self.value and other.value)
    #
    # def __or__(self, other):
    #     return Value(self.value or other.value)

    def __contains__(self, item):
        return Value(item in self.value)

    # def __bool__(self):
    #     print("test")
    #     return self.value is True

    def __eq__(self, other):
        return Value(self.value == other.value)

    def __ne__(self, other):
        return Value(self.value != other.value)

    def __gt__(self, other):
        return Value(self.value > other.value)

    def __ge__(self, other):
        return Value(self.value >= other.value)

    def __lt__(self, other):
        return Value(self.value < other.value)

    def __le__(self, other):
        return Value(self.value <= other.value)
