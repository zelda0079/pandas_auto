

from typing import Any, Callable, List

from .UIModl import FunModel

from .Args import AbcArgs


class CusFunsWrapper(object):
    def __init__(self, org_func) -> None:
        self.org_func = org_func


class HandleWrapper(CusFunsWrapper):

    @staticmethod
    def create_if_not(func) -> 'HandleWrapper':
        if not isinstance(func, HandleWrapper):
            func = HandleWrapper(func)
        return func

    def __init__(self, org_func) -> None:
        super().__init__(org_func)
        self.handle_func: Callable = None
        self.fun_name: str = None
        self.ui_json_func: Callable = None
        self.code_func: Callable = None
        self.args: List[AbcArgs] = []

    def auto_create_ui_func(self):
        if self.ui_json_func is not None:
            return

        def _ui_json_func() -> FunModel:
            fm = FunModel(self.fun_name)
            for a in self.args:
                fm.add_content(a.to_content())

            return fm

        self.ui_json_func = _ui_json_func


def dt_handle_func(fun_name=None, ui_json_func=None):

    def wrapper(func):
        func = HandleWrapper.create_if_not(func)

        func.handle_func = func.org_func
        func.fun_name = fun_name
        func.ui_json_func = ui_json_func
        return func

    return wrapper


def dt_args(**kwargs):

    def wrapper(func):
        func = HandleWrapper.create_if_not(func)

        func.args.extend((arg.set_var_name(var_name)
                          for var_name, arg in kwargs.items()))
        return func

    return wrapper


def dt_source_code(generate_func: Callable):
    def wrapper(func):
        func = HandleWrapper.create_if_not(func)
        func.code_func = generate_func

        return func

    return wrapper
