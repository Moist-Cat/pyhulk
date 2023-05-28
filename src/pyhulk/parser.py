from typing import Union

class DataValidator:

    type_: type
    _val = None

    def __init__(self, type_):
        self._type = type_

    def __get__(self, obj, objtype=None):
        return self._val


    def __set__(self, obj, value):
        if not isinstance(value, self.type_):
            raise ValueError(
                f"type {self._type} expected found '{value.__class__.__name__}' for {value}"
            )
        self._val = type_(value)

class Context:

    _dict: dict

    def __init__(self):
        self._dict = {}

    def __setitem__(self, key, value):
        self._dict.__setitem__(key, value)

    def __getitem__(self, key):
        return self._dict.__getitem__(key)

class AST:
    """
    Master class for expressions
    """

    def eval(self, ctx: "Context"):
        raise NotImplementedError()


class Literal(Expression):
    _val: Union[float, int, str]

    def __init__(self, value):
        self._val = value

    def eval(self, ctx):
        return self._val

class StrLiteral(Literal):
    _val: str = DataValidator(str)

class IntLiteral(Literal):
    _val: str = DataValidator(int)

class FloatLiteral(Literal):
    _val: str = DataValidator(float)
