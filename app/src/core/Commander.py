from typing import List

import uuid

from .Statement import AbcStatement, CodeStatement, Statement

from ..helper.utils import CanJson
import itertools


class Commander(CanJson):

    def to_json_dict(self):
        ret = self.__dict__.copy()
        del ret['statements']
        ret.update({'hasError': self.has_exception()})
        ret.update({'code': self.to_code()})
        return ret

    def __init__(self, name: str) -> None:
        self._id = uuid.uuid1()
        self.name = name
        self.statements: List[AbcStatement] = []

    def __enter__(self) -> 'Commander':
        return self

    def __exit__(self, type, value, trace):
        pass

    @property
    def id(self):
        return self._id

    def create_statement(self, caller_name: str, ret_name: str = None) -> Statement:
        st = Statement(caller_name, ret_name)
        self.addStatement(st)
        return st

    def create_code_statement(self, code) -> CodeStatement:
        st = CodeStatement(code)
        self.addStatement(st)
        return st

    def get_last_statement(self) -> AbcStatement:
        return self.statements[-1]

    def has_exception(self):
        ret = any(s.has_exception() for s in self.statements)
        return ret

    def is_empty(self) -> bool:
        return len(self.statements) == 0

    def addStatement(self, statement: AbcStatement):
        self.statements.append(statement)

    def to_code(self) -> str:
        codes = (
            c.to_code()
            for c in self.statements
        )

        codes = itertools.chain([f'#{self.name}'], codes)

        code = '\n'.join(codes)

        return code


class CommanderManager():

    def __init__(self) -> None:
        self._cmds: List[Commander] = []
        self.reset_cmds()
        self.var_dict = {}

    def get_last_cmd(self) -> Commander:
        if len(self._cmds) == 0:
            return None
        return self._cmds[-1]

    def get_cmds(self):
        return (c for c in self._cmds if not c.is_empty())

    def addVar(self, var_name: str, ret):
        self.var_dict[var_name] = ret

    def getVar(self, var_name: str):
        return self.var_dict[var_name]

    def get_last_used_var_ret(self):
        key = list(self.var_dict.keys())[-1]
        return self.getVar(key)

    def clear_all_var(self):
        self.var_dict.clear()

    def clear_all(self):
        self._cmds.clear()
        self.clear_all_var()

    def append(self, cmd: Commander):
        self._cmds.append(cmd)

    def reset_cmds(self):
        self._cmds: List[Commander] = []

    def remove_cmd(self, id: uuid.UUID):
        idxs = [i for i, t in enumerate(self._cmds) if t.id == id]
        assert (len(idxs) in [0, 1]), f'多个 cmd[id={id}] 符合条件'
        if len(idxs) > 0:
            del self._cmds[idxs[0]]

    def to_code(self) -> str:
        codes = (
            f'{c.to_code()}'
            for c in self.get_cmds()
            if not c.is_empty()
        )

        return '\n\n'.join(codes)
