# -*- coding: utf-8 -*-
from flask import (
    jsonify
)
from myolap.utils.const import _const
import time

def json_result(result, code=0,message='ok',success=True):
    data = {
        "code": code,
        "message": message,
        "result":  result,
        "success": success,
        "timestamp": int(time.time())
    }
    return  jsonify(data)



# def get_column_type(df,col):
#     # 需要进一步完善
#     r= _const.SQL_FIELD_TYPE_STR
#     str_dtype = df[col].dtype
#     if str_dtype.startswith('datetime'):
#         r=_const.SQL_FIELD_TYPE_DATE
#     elif str_dtype.startswith('int') \
#             or str_dtype.startswith('float'):
#         r = _const.SQL_FIELD_TYPE_NUM
#
#     else:
#         pass
#
#     # if isinstance(col,str):
#     #     r=_const.SQL_FIELD_TYPE_STR
#     # elif isinstance(col,str):
#     #     r=''
#     # else:
#     #     r=_const.SQL_FIELD_TYPE_NUM
#
#
#     return r


