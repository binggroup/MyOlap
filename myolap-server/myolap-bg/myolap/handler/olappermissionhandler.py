# -*- coding: utf-8 -*-

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify,current_app
)
import json,time
from myolap.dataquery import dbhelper
from myolap.handler import json_result
from myolap.utils.funcutils import get_sql_field,get_pandas_express
from myolap.utils.const import _const

import pandas as pd

handler = Blueprint('olappermission', __name__)


@handler.route("/olap/olappermission/add", methods=['POST'])
def olappermission_add():
    # 配置权限

    result = 'fail'
    code = 0
    message = '保存失败';
    success = False

    from myolap.utils.authutils import get_current_username
    current_username = get_current_username()
    if current_username is None or current_username.strip() != 'admin':
        #不是登录用户
        return json_result(result=result, code=0, message='无操作权限',success=False)

    formdata = json.loads(request.get_data())
    olap_id = formdata['olap_id']
    username = formdata['username']

    from myolap.model.sysdbmodel import OlapDimensionPermission, multi_to_list, multi_to_list_by_columns
    try:
        u = g.session.query(OlapDimensionPermission).filter(OlapDimensionPermission.username == username).filter(OlapDimensionPermission.olap_id == olap_id).first()

        if u is None:
            # 新增
            u = OlapDimensionPermission()
            u.olap_id = formdata['olap_id']
            g.session.add(u)

        #更新字段内容
        u.username = formdata['username']
        u.col_permission = json.dumps(formdata['col_permission'])
        u.row_permission = json.dumps(formdata['row_permission'])

        u.create_by = current_username
        u.version = formdata['version']
        g.session.commit()
        result = 'ok'
        message = '保存成功'
        success = True
    except Exception as e:
        message = 'error: %s' %(e)
        current_app.logger.error('error: %s' %(e))

    return json_result(result=result, code=0, message=message,success=success)


@handler.route("/olap/olappermission/delete", methods=['DELETE'])
def olappermission_delete():
    # 删除某张多维表
    result = 'fail'
    code = 0
    message = '保存失败';
    success = False
    from myolap.utils.authutils import get_current_username
    current_username = get_current_username()
    if current_username is None or current_username.strip() != 'admin':
        # 不是登录用户
        return json_result(result=result, code=0, message='无操作权限', success=False)

    olap_id = request.args.get("olap_id")
    usernames = request.args.get("usernames").split(',')
    if olap_id is None or usernames is None:
        return json_result(result=result, code=0, message='参数无效', success=False)

    from myolap.model.sysdbmodel import OlapDimensionPermission
    try:
        if len(usernames)> 0:
            for username in usernames:
                g.session.query(OlapDimensionPermission).filter(OlapDimensionPermission.olap_id == olap_id).filter(OlapDimensionPermission.username == username).delete()
            g.session.commit()
        result ='OK'
        message = '删除成功'
        success = True
    except Exception as e:
        message = 'error: %s' %(e)
        current_app.logger.error('error: %s' %(e))

    return json_result(result=result, code=0, message=message,success=success)


# @handler.route("/olap/olappermission/getuserlist", methods=['GET'])
# def olappermission_getuserlist():
#     #获取某个olap多维表的权限列表
#     olap_id = request.args.get("olap_id")
#     from myolap.model.sysdbmodel import OlapDimensionPermission,multi_to_list_by_columns
#     modellist= g.session.query(OlapDimensionPermission).with_entities(OlapDimensionPermission.username, OlapDimensionPermission.olap_id).filter(OlapDimensionPermission.olap_id==olap_id).all()
#     list = multi_to_list_by_columns(modellist, ['olap_id','username'])
#
#     message = '查询信息成功'
#
#     return json_result(list, code=0, message=message)


# @handler.route("/olap/olappermission/get", methods=['GET'])
# def olappermission_get():
#     # 获取某个olap多维表的权限列表
#     olap_id = request.args.get("olap_id")
#     username = request.args.get("username")
#
#     from myolap.model.sysdbmodel import OlapDimensionPermission, multi_to_list_by_columns
#     u = g.session.query(OlapDimensionPermission).filter(OlapDimensionPermission.olap_id == olap_id).filter(OlapDimensionPermission.username == username).first()
#     if u is None:
#         result = {
#             "col_permission": [],
#             "row_permission": [],
#             "username": username,
#             "olap_id": olap_id
#         }
#     else:
#         result = {
#             "col_permission": u.col_permission,
#             "row_permission": u.row_permission,
#             "username": username,
#             "olap_id": olap_id
#         }
#     message = '查询信息成功'
#
#     return json_result(result, code=0, message=message)