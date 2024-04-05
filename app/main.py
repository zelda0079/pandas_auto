from flask import Flask
import flask
from flask import request
import pandas as pd
import numpy as np
import json
import traceback
import sys
from src.cusFuns.core.FunsPool import auto_register

from src.helper.utils import json_converter
from src.dataModel.pandasCmd import PandasCmd
from src.core.Proxy import ProxyManager

import webbrowser
import os


m_proxys = ProxyManager()
auto_register(r'src/cusFuns')

app = Flask(__name__,
            template_folder='./web/templates',
            static_folder='./web/static')


@app.errorhandler(Exception)
def error_handler(ex):
    exc_type, exc_value, exc_traceback_obj = sys.exc_info()
    return {
        'type':
        'error',
        'code':
        traceback.format_exception(exc_type,
                                   exc_value,
                                   exc_traceback_obj,
                                   limit=2),
        'message':
        repr(ex)
    }


def get_data_from_post():
    return json.loads(flask.request.get_data().decode())


@app.route('/')
def index():
    return flask.render_template('index.html')


@app.route('/api/get_file_args/ext=<ext>', methods=['get'])
def get_file_args(ext: str):
    print(ext)
    print(request.values.get('ext'))
    return 'done'


@app.route('/api/upload_file', methods=['post'])
def upload_file():

    file = flask.request.files.get('file')

    ext = flask.request.form['ext']
    filename = flask.request.form['file_name']
    args = json.loads(flask.request.form['args'])

    # todo:根据不同情况做处理
    m_proxys.read_data(file, filename, ext, args)
    return df2json(m_proxys.get_df_data())


@app.route('/api/query', methods=['post'])
def query():
    param = get_data_from_post()
    m_proxys.query(param['query'])
    return df2json(m_proxys.get_df_data())


@app.route('/api/table/filters', methods=['post'])
def table_filters():
    param = get_data_from_post()
    m_proxys.query(param['query'])
    return df2json(m_proxys.get_df_data())


@app.route('/api/table/handle', methods=['post'])
def table_handle():

    # todo:重构
    def _to_df_cols(df: pd.DataFrame, col: str):
        # 如果是多层索引，使用eval转成元组
        if isinstance(df.columns, pd.MultiIndex):
            return eval(col)

        return col

    param = get_data_from_post()

    filters = param['filters']
    sort = param['sort']

    print(filters, sort)

    filters = ((f['field'], f['values']) for f in filters)
    m_proxys.filter(filters)

    df_ret = m_proxys.get_df_data()

    if sort:
        order = True if sort['order'] == 'asc' else False
        df_ret = df_ret.sort_values(_to_df_cols(
            df_ret, sort['field']), ascending=order)

    return df2json(df_ret)


@app.route('/api/groupby', methods=['post'])
def groupby():
    param = get_data_from_post()
    keys = param['_keys']
    aggs = param['_aggs']

    aggs = {d['filed']: d['methods'] for d in aggs}

    m_proxys.groupby(keys, aggs)

    return df2json(m_proxys.get_df_data())


@app.route('/api/remove/cmd', methods=['post'])
def remove_cmd():
    param = get_data_from_post()
    id = param['id']

    m_proxys.remove_cmd(id)
    return df2json(m_proxys.get_df_data())


@app.route('/api/py_cody')
def get_py_code():
    ret = m_proxys.to_code()
    return ret


@app.route('/api/cmds')
def get_cmds():
    cmds = m_proxys.get_cmds()
    res = flask.json.dumps(cmds, default=json_converter)
    return res


def df2json(df: pd.DataFrame, head_tail_num=10):

    ret = None

    if len(df) > (head_tail_num * 2):
        ret = pd.concat([df.head(head_tail_num), df.tail(head_tail_num)])
    else:
        ret = df

    cmd = PandasCmd.from_df(df, ret)
    ret = flask.json.dumps(cmd, default=json_converter)
    return ret


@app.route('/api/cus_fun', methods=['post'])
def cus_fun():
    param = get_data_from_post()
    data = param['data']

    m_proxys.run_cus_fun(data)

    return df2json(m_proxys.get_df_data())


@app.route('/api/cus_fun/desc')
def get_cus_funcs_desc():
    ret = m_proxys.get_cus_funcs_desc()
    ret = flask.json.dumps(ret, default=json_converter)
    return ret


@app.route('/api/cus_fun/model', methods=['get'])
def get_cus_funcs_ui_model():

    uid = str(request.args.get('uid'))

    ret = m_proxys.get_ui_model(uid)
    ret = flask.json.dumps(ret, default=json_converter)
    return ret


@app.route('/api/cus_fun/input', methods=['post'])
def get_cus_funcs_input():
    param = get_data_from_post()
    data = param['data']

    m_proxys.input_cus_funcs(data)
    return df2json(m_proxys.get_df_data())


def main():
    port = 5551

    # The reloader has not yet run - open the browser
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        webbrowser.open_new(f'http://localhost:{port}/')

    # Otherwise, continue as normal
    app.run(host="localhost", port=port)


if __name__ == '__main__':
    main()
