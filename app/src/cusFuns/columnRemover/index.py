from ..core.DecoratorFuns import dt_handle_func, dt_args
from ..core import Args as ty
import pandas as pd


@dt_handle_func('删除列')
@dt_args(org_name=ty.ColumnSelect('待删除的列：'))
def remove_cols(df: pd.DataFrame, org_name: str):
    return df.drop(columns=org_name)
