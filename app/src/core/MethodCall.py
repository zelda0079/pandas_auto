from typing import List
from .CodeFormatter import CodeFormatter, GetItemCodeFormatter, MethodCodeFormatter, OperatorCodeFormatter

from ..helper.utils import CanJson


class ArgAbc(object):

    def get_runtime_value(self, var_dict):
        raise NotImplementedError


class ArgActor(ArgAbc):

    def __init__(self, org_value, str_value: str) -> None:
        self.org_value = org_value
        self.str_value = str_value

    def get_runtime_value(self, var_dict):
        return self.org_value

    def __str__(self) -> str:
        return CodeFormatter.type2str(self.str_value)


class ArgVar(ArgAbc):

    def __init__(self, var_name) -> None:
        self.var_name = var_name

    def get_runtime_value(self, var_dict):
        return var_dict[self.var_name]

    def __str__(self) -> str:
        return self.var_name


class MethodCall(CanJson):

    def to_json_dict(self):
        # return CanJson.dict_keep_items(self, self.__dict__, ['name', 'args', 'kwargs'])
        return {
            'desc': self.to_code()
        }

    def __init__(self, name) -> None:
        self.name = name
        self.formatter = MethodCodeFormatter()
        self.args = tuple()
        self.kwargs = {}
        self._ex = None

        self._on_after_call_func = lambda call: None

    def on_after_call(self, func):
        self._on_after_call_func = func

    def set_args(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __str__(self) -> str:
        return f'name:{self.name};args:{self.args};kws:{self.kwargs}'

    @property
    def has_ex(self) -> bool:
        return self._ex != None

    @property
    def ex(self):
        return self._ex

    def set_exception(self, ex: Exception):
        self._ex = ex

    def to_code(self):
        return self.formatter.to_code(self.name, self.args, self.kwargs)

    def run(self, obj, var_dict):

        args = [
            a if not isinstance(a, ArgAbc) else a.get_runtime_value(var_dict)
            for a in self.args
        ]

        kws = {
            k: (v if not isinstance(v, ArgAbc)
                else v.get_runtime_value(var_dict))
            for k, v in self.kwargs.items()
        }

        return getattr(obj, self.name)(*args, **kws)


class GetItemMethodCall(MethodCall):

    def __init__(self) -> None:
        super().__init__('__getitem__')
        self.formatter = GetItemCodeFormatter()


class OperatorMethodCall(MethodCall):

    def __init__(self, operator, call_name) -> None:
        '''
        operator : '&' , '|' , '==' 
        '''
        super().__init__(call_name)
        self.operator = operator
        self.formatter = OperatorCodeFormatter()

    def to_code(self):
        return self.formatter.to_code(self.operator, self.args, self.kwargs)


class AndOperatorMethodCall(OperatorMethodCall):

    def __init__(self) -> None:
        super().__init__('&', '__and__')


class OrOperatorMethodCall(OperatorMethodCall):

    def __init__(self) -> None:
        super().__init__('|', '__or__')


class EqualOperatorMethodCall(OperatorMethodCall):

    def __init__(self) -> None:
        super().__init__('==', '__eq__')
