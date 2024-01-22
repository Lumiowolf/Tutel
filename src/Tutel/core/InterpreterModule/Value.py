from typing import Generic, TypeVar

from Tutel.common.JsonSerializable import JsonSerializable

T = TypeVar("T")


class ValueIterator:
    def __init__(self, obj: "Value"):
        self._value_obj = obj
        self._index = 0

    def __next__(self):
        if self._index < len(self._value_obj):
            result = self._value_obj[self._index]
            if type(result) != Value:
                result = Value(result)
            self._index += 1
            return result
        raise StopIteration


class Value(Generic[T], JsonSerializable):
    def __init__(self, value: T) -> None:
        self.value: T = value

    def append(self, val) -> None:
        self.value.append(val)

    def to_json(self):
        return self.value

    def __call__(self, *args, **kwargs):
        return self.value(*args, **kwargs)

    def __getitem__(self, item):
        return self.value[item] if type(self.value[item]) == Value else Value(self.value[item])

    def __getattr__(self, item):
        return getattr(self.value, item)

    def __len__(self):
        return len(self.value)

    def __iter__(self):
        return ValueIterator(self)

    def __neg__(self):
        return Value(-self.value)

    def __add__(self, other):
        return Value(self.value + other.value)

    def __iadd__(self, other) -> None:
        self.value += other.value

    def __sub__(self, other):
        return Value(self.value - other.value)

    def __isub__(self, other) -> None:
        self.value -= other.value

    def __mul__(self, other):
        return Value(self.value * other.value)

    def __imul__(self, other) -> None:
        self.value *= other.value

    def __truediv__(self, other):
        return Value(self.value / other.value)

    def __idiv__(self, other) -> None:
        self.value /= other.value

    def __floordiv__(self, other):
        return Value(self.value // other.value)

    def __mod__(self, other):
        return Value(self.value % other.value)

    def __imod__(self, other) -> None:
        self.value %= other.value

    def __contains__(self, item) -> bool:
        return item in self.value

    def __bool__(self) -> bool:
        return bool(self.value)

    def __eq__(self, other) -> bool:
        return self.value == other.value

    def __ne__(self, other) -> bool:
        return self.value != other.value

    def __gt__(self, other) -> bool:
        return self.value > other.value

    def __ge__(self, other) -> bool:
        return self.value >= other.value

    def __lt__(self, other) -> bool:
        return self.value < other.value

    def __le__(self, other) -> bool:
        return self.value <= other.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return str(self)

    def __int__(self) -> int:
        return int(self.value)

    def __abs__(self) -> int:
        return abs(self.value)
