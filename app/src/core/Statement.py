

from typing import List
from .MethodCall import AndOperatorMethodCall, EqualOperatorMethodCall, GetItemMethodCall, MethodCall, OrOperatorMethodCall


class AbcStatement(object):

    def has_exception(self) -> bool:
        raise NotImplementedError

    def to_code(self):
        """
        docstring
        """
        raise NotImplementedError

    def run(self, var_dict):
        """
        docstring
        """
        raise NotImplementedError


class CodeStatement(AbcStatement):

    def __init__(self, code) -> None:
        super().__init__()
        self.code = code
        self.ex = None

    def has_exception(self) -> bool:
        return self.ex is not None

    def to_code(self):
        """
        docstring
        """
        return self.code

    def run(self, var_dict):
        obj = None

        try:
            obj = exec(self.code, {}, var_dict)
        except Exception as ex:
            self.ex = ex
            raise

        return None


class Statement(AbcStatement):
    def __init__(self,  caller_name: str, ret_name: str = None) -> None:
        super().__init__()
        self.calls: List[MethodCall] = []
        self.caller_name = caller_name
        self.ret_name = ret_name

    def __getattr__(self, name):
        call = MethodCall(name)
        self.addCall(call)
        return self

    def __call__(self, *args, **kwargs):
        self.calls[-1].set_args(*args, **kwargs)
        return self

    def __getitem__(self, key):
        call = GetItemMethodCall()
        self.addCall(call)
        call.set_args(key)
        return self

    def __or__(self, other):
        call = OrOperatorMethodCall()
        self.addCall(call)
        call.set_args(other)
        return self

    def __and__(self, other):
        call = AndOperatorMethodCall()
        self.addCall(call)
        call.set_args(other)
        return self

    def __eq__(self, other):
        call = EqualOperatorMethodCall()
        self.addCall(call)
        call.set_args(other)
        return self

    def has_exception(self) -> bool:
        ret = any(c.has_ex for c in self.calls)
        return ret

    def addCall(self, call: MethodCall):
        self.calls.append(call)

    def is_empty(self) -> bool:
        return len(self.calls) == 0

    def get_calls(self):
        return (c for c in self.calls if c.name != '__iter__')

    def to_code(self) -> str:
        codes = (
            c.to_code()
            for c in self.calls
        )

        code = ''.join(codes)

        if self.ret_name:
            return f'{self.ret_name} = {self.caller_name}{code}'

        return f'{self.caller_name}{code}'

    def run(self, var_dict):

        obj = var_dict[self.caller_name]

        for c in self.get_calls():
            try:
                obj = c.run(obj, var_dict=var_dict)
                if self.ret_name:
                    var_dict[self.ret_name] = obj
            except Exception as ex:
                c.set_exception(ex)
                raise
