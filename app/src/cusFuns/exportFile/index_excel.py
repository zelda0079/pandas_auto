from ..core.DecoratorFuns import dt_handle_func, dt_args, dt_source_code
from ..core import Args as ty
import pandas as pd


def generate_code(*args, **kwargs):
    return f'''df.to_excel(r'{kwargs['path']}','{kwargs['sheet_name']}',index={kwargs['index']})'''


@dt_source_code(generate_code)
@dt_handle_func('导出文件-Excel')
@dt_args(path=ty.Input('文件全路径：'), sheet_name=ty.Input('工作表名字：'), index=ty.Switch('是否输出行索引：', default=False))
def remove_cols(df: pd.DataFrame, path, sheet_name, index):
    return df.to_excel(path, sheet_name)
