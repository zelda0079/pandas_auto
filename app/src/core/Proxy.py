
from typing import Dict, Iterable, List

from ..cusFuns.core.UIModl import CusFunInputRet, FunModel, InputRet

from ..cusFuns.core.FunsPool import FunsPool

from .CodeFormatter import CodeFormatter

from .MethodCall import AndOperatorMethodCall, ArgActor, ArgVar, EqualOperatorMethodCall, MethodCall, GetItemMethodCall, OrOperatorMethodCall
from .Commander import Commander, CommanderManager, Statement
import pandas as pd
import uuid


class Proxy(object):
    def __init__(self) -> None:
        self.cmdManager = CommanderManager()

    def with_cmd(self, name: str = '') -> Commander:
        cmd = Commander(name)
        self.cmdManager.append(cmd)
        return cmd

    def __getattr__(self, name):
        st = self.cmdManager.get_last_cmd().get_last_statement()
        call = MethodCall(name)
        st.addCall(call)
        return st

    def __getitem__(self, key):
        st = self.cmdManager.get_last_cmd().get_last_statement()
        call = GetItemMethodCall()
        st.addCall(call)
        call.set_args(key)
        return st

    def __or__(self, other):
        st = self.cmdManager.get_last_cmd().get_last_statement()
        call = OrOperatorMethodCall()
        st.addCall(call)
        call.set_args(other)
        return st

    def __and__(self, other):
        st = self.cmdManager.get_last_cmd().get_last_statement()
        call = AndOperatorMethodCall()
        st.addCall(call)
        call.set_args(other)
        return st

    def __eq__(self, other):
        st = self.cmdManager.get_last_cmd().get_last_statement()
        call = EqualOperatorMethodCall()
        st.addCall(call)
        call.set_args(other)
        return st

    def to_code(self):
        return self.cmdManager.to_code()


class CallerProxy(Proxy):

    def __init__(self) -> None:
        super().__init__()

    def set_obj_to_var(self, var_name: str, obj):
        self.cmdManager.addVar(var_name, obj)

    def run(self, res_var_name: str):

        obj = None
        var_dict = self.cmdManager.var_dict

        for cmd in self.cmdManager.get_cmds():

            for s in cmd.statements:
                s.run(var_dict)

        if res_var_name:
            return self.cmdManager.getVar(res_var_name)


class ProxyManager(object):

    s_read_func_mapping = {
        'xlsx': 'read_excel',
        'xls': 'read_excel',
        'xlsm': 'read_excel',
        'csv': 'read_csv',
        'feather': 'read_feather',
    }

    s_engine_map = {
        'xls': 'xlrd',
        'xlsx': 'openpyxl',
        'xlsm': 'openpyxl'
    }

    def __init__(self) -> None:
        self.df_proxy = CallerProxy()
        self.pd_read_proxy = CallerProxy()
        self.source_cache: pd.DataFrame = None

    def _get_all_proxys(self) -> Iterable[CallerProxy]:
        yield self.pd_read_proxy
        yield self.df_proxy

    @staticmethod
    def add_read_kws_for_excel(file_ext, kws):
        if file_ext in ProxyManager.s_engine_map:
            kws['engine'] = ProxyManager.s_engine_map[file_ext]

        return kws

    def read_data(self, file, filename, file_ext, read_kws):
        self.df_proxy.cmdManager.clear_all()
        self.pd_read_proxy.cmdManager.clear_all()

        pd_px = self.pd_read_proxy

        with pd_px.with_cmd('导入模块') as cmd:
            cmd.create_code_statement('import pandas as pd')

        with pd_px.with_cmd('加载数据') as cmd:
            ProxyManager.add_read_kws_for_excel(file_ext, read_kws)
            cmd.create_statement('pd', 'df')
            func_name = ProxyManager.s_read_func_mapping[file_ext]
            getattr(pd_px, func_name)(ArgActor(file, filename), **read_kws)

        df = pd_px.run('df')
        self.source_cache = df

        # 表头有任何不是str，转str
        if (df.columns.to_series().map(type) != str).any():
            with self.df_proxy.with_cmd('表头统一转文本') as cmd:
                cmd.create_code_statement(
                    '''cols = [str(c) for c in df.columns]
df.columns=cols''')

    def get_df_data(self) -> pd.DataFrame:
        self.df_proxy.set_obj_to_var('df', self.source_cache)
        ret = self.df_proxy.run('df')
        self.df_proxy.cmdManager.clear_all_var()
        self.df_proxy.set_obj_to_var('pd', pd)
        return ret

    def query(self, query_str: str):
        df_px = self.df_proxy

        with df_px.with_cmd('筛选') as cmd:
            cmd.create_statement('df', 'df')
            df_px.query(query_str)

    def groupby(self, keys, aggs):
        df_px = self.df_proxy

        with df_px.with_cmd('分组统计') as cmd:
            cmd.create_statement('df', 'df')
            df_px.groupby(keys).agg(aggs).reset_index()

    def filter(self, filters):
        """
        filters : [(字段名,值list)]
        [('name',[1,2,3]),('age',[10,20,30])]
        """

        def _get_code(name, values):
            name = CodeFormatter.type2str(name)
            if len(values) > 1:
                return f'(df[{name}].isin({values}))'

            return f'(df[{name}] == {CodeFormatter.type2str(values[0])})'

        df_px = self.df_proxy
        cmd_name = '筛选(表格操作)'
        last_cmd = df_px.cmdManager.get_last_cmd()

        if (last_cmd is not None) and last_cmd.name == cmd_name:
            df_px.cmdManager.remove_cmd(last_cmd._id)

        filters = list(_get_code(name, values) for name, values in filters)
        cond_code = ' & '.join(filters)

        if len(filters) == 0:
            return

        with self.df_proxy.with_cmd(cmd_name) as cmd:
            cmd.create_code_statement(
                '''cond = {cond}
df = df[cond]'''.format(cond=cond_code))

    def run_cus_fun(self, data):
        print(data)

    def _get_all_cmds(self) -> Iterable[Commander]:
        return (
            m
            for p in self._get_all_proxys()
            for m in p.cmdManager.get_cmds()
        )

    def get_cmds(self) -> List[Commander]:
        cmds = list(self._get_all_cmds())
        return cmds

    def get_ui_model(self, uid: str):
        return FunsPool.get_once().get_ui_model(uid)

    def get_cus_funcs_desc(self):
        ret = FunsPool.get_once().get_all_desc()
        return ret

    def input_cus_funcs(self, data: Dict):

        input_ret = CusFunInputRet.from_dict(data)

        uid = input_ret.uid
        cf = FunsPool.get_once().get_cusFunc(uid)

        input_args = {
            c.var_name: c.input
            for c in input_ret.contents
        }

        with self.df_proxy.with_cmd(cf.fun_name) as cmd:
            code = cf.to_code(**input_args)
            cmd.create_code_statement(code)

    def remove_cmd(self, cmd_id: str):
        for p in self._get_all_proxys():
            p.cmdManager.remove_cmd(uuid.UUID(cmd_id))

    def to_code(self) -> str:
        codes = (
            p.to_code()
            for p in self._get_all_proxys()
        )

        ret = '\n\n'.join(codes)
        return ret
