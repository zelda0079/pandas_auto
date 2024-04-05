

from typing import Callable, Dict
import uuid
import pathlib
import importlib
import inspect
import os


from ..core.DecoratorFuns import CusFunsWrapper, HandleWrapper
from .UIModl import FunModel


class CusFunc(object):
    """
    docstring
    """
    pass

    def __init__(self) -> None:
        self.call_func: Callable = None
        self.uid: str = None
        self.ui_json_func: Callable = None
        self.code_func: Callable = None
        self.fun_name: str = None

        self.reset_uid()

    def reset_uid(self):
        self.uid = str(uuid.uuid1().int)

    def get_ui_json_model(self) -> FunModel:
        fm: FunModel = self.ui_json_func()
        fm.uid = self.uid
        return fm

    def run(self, data):
        """
        docstring
        """
        pass

    @staticmethod
    def _drop_decoreator(code: str) -> str:
        lines = code.split('\n')
        lines = [n for n in lines if n and n[0] != '@']
        return '\n'.join(lines)

    def to_code(self, *args, **kwargs) -> str:
        if self.code_func:
            return self.code_func(*args, **kwargs)

        def_code = inspect.getsource(self.call_func)
        def_code = CusFunc._drop_decoreator(def_code)

        func_name = self.call_func.__name__
        call_code = f'''df = {func_name}(df,*{args},**{kwargs})'''
        return '\n'.join([def_code, call_code])


class FunsPool(object):
    s_instance: 'FunsPool' = None

    @staticmethod
    def get_once() -> 'FunsPool':
        FunsPool.s_instance = FunsPool.s_instance or FunsPool()
        return FunsPool.s_instance

    def __init__(self) -> None:
        self._mapping: Dict[str, CusFunc] = {}

    def register(self, cusFunc: CusFunc):
        self._mapping[cusFunc.uid] = cusFunc

    def get_cusFunc(self, uid: str) -> CusFunc:
        return self._mapping[uid]

    def get_all_desc(self):
        def _to_dict(fm: FunModel):
            return {
                'function_name': fm.function_name,
                'uid': fm.uid
            }

        models = (cf.get_ui_json_model() for cf in self._mapping.values())

        ret = [_to_dict(f)
               for f in models]
        return ret

    def get_ui_model(self, uid: str):
        ret = self.get_cusFunc(uid).get_ui_json_model()
        return ret


def _register_module(module_path: str):
    '''
    module_path : str 
    'src.cusFuns.columnNameChanger.columnNameChanger'
    '''
    module = importlib.import_module(module_path)
    # [('name',obj)]
    funcs = [(name, func) for name, func in module.__dict__.items()
             if isinstance(func, CusFunsWrapper)]

    cf = CusFunc()

    for name, func in funcs:
        if isinstance(func, HandleWrapper):
            func.auto_create_ui_func()

            cf.call_func = func.handle_func
            cf.ui_json_func = func.ui_json_func
            cf.fun_name = func.fun_name or '未命名操作'
            cf.code_func = func.code_func

    FunsPool.get_once().register(cf)


def auto_register(base_folder: str):
    files = (p for p in pathlib.Path(base_folder).glob('*/*.py')
             if p.parent.parts[-1] != 'core')

    for md_name in files:
        md_name = str(md_name)[:-3]
        md_name = md_name.replace(os.path.sep, '.')

        _register_module(md_name)
