from ..core.DecoratorFuns import dt_handle_func, dt_args, dt_source_code
from ..core import Args as ty
import pandas as pd


def generate_code(*args, **kwargs):
    return f'''df.to_feather(r'{kwargs['path']}')'''


@dt_source_code(generate_code)
@dt_handle_func('导出文件-feather')
@dt_args(path=ty.Input('文件全路径：'))
def remove_cols(df: pd.DataFrame, path):
    return df.to_feather(path)
