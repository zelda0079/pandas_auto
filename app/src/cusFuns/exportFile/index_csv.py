from ..core.DecoratorFuns import dt_handle_func, dt_args, dt_source_code
from ..core import Args as ty
import pandas as pd

m_encoding = ['utf8', 'gb2312', 'gbk']


def generate_code(*args, **kwargs):
    encoding = m_encoding[kwargs['encoding']]
    return f'''df.to_csv(r'{kwargs['path']}',encoding='{encoding}',index={kwargs['index']})'''


@dt_source_code(generate_code)
@dt_handle_func('导出文件-csv')
@dt_args(path=ty.Input('文件全路径：'), encoding=ty.Select('编码：', m_encoding, default='utf8'), index=ty.Switch('是否输出行索引：', default=False))
def remove_cols(df: pd.DataFrame, path, encoding, index):
    return df.to_csv(path, encoding=encoding, index=index)
