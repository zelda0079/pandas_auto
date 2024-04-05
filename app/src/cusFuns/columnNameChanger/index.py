from ..core.DecoratorFuns import dt_handle_func, dt_args, dt_source_code
from ..core import Args as ty
import pandas as pd


def generate_code(*args, **kwargs):
    kws = {kwargs['org_name']: kwargs['new_name']}
    return f'''df = df.rename(columns={kws})'''


@dt_source_code(generate_code)
@dt_handle_func('修改列名')
@dt_args(org_name=ty.ColumnSelect('待修改列：'), new_name=ty.Input('新列名：', placeholder='输入新的列名'))
def change_column_name(df, org_name, new_name):
    return df.rename(columns={org_name: new_name})
