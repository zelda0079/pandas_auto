from enum import Enum
from typing import Dict, List
from ..helper.utils import CanJson
import pandas as pd

_m_ui_col_type_mapping = {
    'object': 'str',
    'int': 'number',
    'int64': 'number',
    'int32': 'number',
    'datetime64[ns]': 'datetime'
}


def to_ui_col_type(org_type):
    stype = str(org_type)
    ret = _m_ui_col_type_mapping.get(stype, stype)
    return ret


class CmdType(Enum):
    Success = 'success'
    Error = 'error'


class FilterItem(CanJson):
    def __init__(self, label, value) -> None:
        self.text = label
        self.value = value


class Field(CanJson):
    @staticmethod
    def from_df(org_df: pd.DataFrame, out_df: pd.DataFrame) -> List['Field']:
        def _get_filters(col: pd.Series) -> List[FilterItem]:

            col_values = col.drop_duplicates().fillna('空格')[:50]

            return [
                FilterItem(v, v) for v in col_values
            ]

        if isinstance(out_df.columns, pd.MultiIndex):
            ret = []
            for k, g in out_df.columns.to_frame().groupby(0, sort=False):
                fat_f = Field(k).set_sorter(False)

                sub_fs = [
                    Field(c, str((k, c))).set_filter(
                        _get_filters(org_df[(k, c)]))
                    for c in g[1]
                ]
                fat_f.set_children(sub_fs)
                ret.append(fat_f)
            return ret

        return [
            Field(c, c).set_filter(_get_filters(org_df[c])) for c in out_df.columns
        ]

    def __init__(self, title: str, field: str = None) -> None:
        self.title: str = title
        self.dataIndex: str = field
        self.children: List[Field] = None
        self.filters: List[FilterItem] = None
        self.showOverflow: bool = True
        self.sorter = True
        self.filterMultiple = True

    def set_children(self, fields: List['Field']):
        self.children = fields

    def set_sorter(self, value: bool) -> 'Field':
        self.sorter = value
        return self

    def set_filter(self, filters: List[FilterItem]) -> 'Field':
        self.filters = filters
        return self


class Table(CanJson):
    @staticmethod
    def from_df(org_df: pd.DataFrame, out_df: pd.DataFrame) -> 'Table':

        fields = Field.from_df(org_df, out_df)

        # df_copy = df.copy()

        if isinstance(out_df.columns, pd.MultiIndex):
            out_df.columns = out_df.columns.to_series().apply(
                lambda x: str(tuple(x)))

        out_df.columns = [str(c) for c in out_df.columns]
        data = out_df.fillna('').to_dict(orient='index')
        data = [
            dict(**{'___key___': k}, **v)
            for k, v in data.items()]

        return Table(fields, data)

    def __init__(self, fields: List[Field], data=[]) -> None:
        self.fields: List[Field] = fields
        self.data: List[Dict] = data

    def addrow(self, data: Dict) -> 'Table':
        self.data.append(data)
        return self

    def set_all_data(self, data: List[Dict]) -> 'Table':
        self.data = data
        return self


class ColumnInfo(CanJson):
    @staticmethod
    def from_df(df: pd.DataFrame) -> List['ColumnInfo']:
        return [
            ColumnInfo(str(c), c, str(t), to_ui_col_type(t))
            for c, t in zip(df.columns, df.dtypes)
        ]

    def __init__(self, field, label, pd_type, ui_type) -> None:
        self.field = field
        self.label = label
        self.type = pd_type
        self.ui_type = ui_type


class PandasCmd(CanJson):
    @staticmethod
    def from_df(org_df: pd.DataFrame, out_df: pd.DataFrame) -> 'PandasCmd':
        table = Table.from_df(org_df, out_df)
        colInfos = ColumnInfo.from_df(org_df)
        return PandasCmd(CmdType.Success, table, colInfos)

    def __init__(self,
                 type: CmdType,
                 table: Table = None,
                 columnInfos: List[ColumnInfo] = []) -> None:
        self.type: CmdType = type
        self.columnInfos: List[ColumnInfo] = columnInfos
        self.table: Table = table or {}
