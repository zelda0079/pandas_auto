
# import pandas as pd


# def to_col_type(org_type):
#     mapping = {
#         'object': 'str',
#         'int': 'number',
#         'int64': 'number',
#         'int32': 'number',
#     }

#     stype = str(org_type)

#     return mapping[stype]


# def get_each_field(df: pd.DataFrame):

#     for c, t in zip(df.columns, df.dtypes):
#         field = c
#         topF = c
#         if isinstance(c, tuple):
#             field = '_'.join(c)
#             topF = c[0]

#         yield topF, {
#             'title': f'{field}[{str(t)}]',
#             'field': field, 'type': to_col_type(t),
#             'filters': []
#         }


# def flat_cols(cols):
#     return [
#         '_'.join(c) if isinstance(c, tuple) else c
#         for c in cols
#     ]


# def columns2fields_obj(df: pd.DataFrame):

#     count = 0
#     pre = None
#     ret = []
#     aggFs = []

#     def _append_ret(aggFs, ret, pre_topf):
#         if len(aggFs) > 0:
#             if len(aggFs) == 1:
#                 ret.append(aggFs[0])
#             else:
#                 ret.append({'title': pre_topf, 'children': aggFs})

#     for topf, field in get_each_field(df):

#         if topf != pre:
#             _append_ret(aggFs, ret, pre)
#             aggFs = []

#         aggFs.append(field)
#         pre = topf

#     _append_ret(aggFs, ret, pre)

#     return ret


# if __name__ == "__main__":
#     df = pd.read_excel('data/test.xlsx')
#     ret = df.groupby(['col1']).agg(
#         {'col2': ['first', 'last'], 'col3': ['first']})
#     fields = columns2fields_obj(ret)
#     print(fields)
