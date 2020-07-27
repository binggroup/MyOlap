# -*- coding: utf-8 -*-

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify,current_app
)
import json
from myolap.dataquery import dbhelper



handler = Blueprint('data', __name__)

@handler.route("/data/testthread")
def testthread():

    a = dbhelper.test_thread();
    print('ok.........')
    return 'ok' + a



@handler.route("/data/testsql")
def testsql():
    # from myolap.app import sysdb
    # from myolap.model.sysdbmodel import SysDataSource
    # # test = SysDataSource(userid='uid',username='haha name')
    # # sysdb.session.add(test)
    # # sysdb.session.commit()
    #
    # u = SysDataSource.query.filter_by(code='adb').first()
    # print(u.code)
    # print(u.name)
    # print(u.db_type)
    # print(u.db_driver)
    # print(u.db_url)
    print('===============1')
    s = dbhelper.get_tempdata('adb')
    print('==============2')
    print(s)
    return  s




@handler.route("/data/test")
def test():
    # dbhelper.init_db()
    sql = "SELECT * FROM h1_first_login limit 10"  # SQL query
    df = dbhelper.get_data_by_dsandsql('mysqltest',sql)
    r = df.to_json(orient="columns",force_ascii=False)
    # r = jsonify(df)
    current_app.logger.info('this is in blueprint dp model...............')
    # return "index hello world"
    return r

#正式查询接口，跟进客户端提交的sql和维度，并行查询db，并跟进维度进行合并
#接口数据格式如下
#{
#     "check_dimension": [
#         {
#             "field_name": "devicetype",
#             "field_type": "1",
#             "type": "0"
#         },
#         {
#             "field_name": "dt_hour",
#             "field_type": "1",
#             "type": "0"
#         }
#     ],
#     "checked_quotas_sql": [
#         {
#             "dsname": "fufei01",
#             "sql": "SELECT gamechannel,serverid,COUNT(DISTINCT userid) AS usercnt FROM h1_first_login WHERE serverid IN ('3990','1301') GROUP BY gamechannel,serverid"
#         },
#         {
#             "dsname": "xinzeng02",
#             "sql": "SELECT gamechannel,serverid,COUNT(DISTINCT deviceid) AS dcnt FROM h1_first_login WHERE serverid IN ('3990','1301') GROUP BY gamechannel,serverid"
#         }
#     ]
# }
@handler.route("/data/query", methods=['POST'])
def query():
    result = ''
    current_app.logger.info('get query...........')
    if request.method == 'POST':
        sql = request.get_data()
        current_app.logger.info(sql)
        j = json.loads(sql)
        result = dbhelper.get_data(j['checked_quotas_sql'],j['check_dimension'])

        #response = {
        #    'state': 200,
        #    'data': result,
        #    'message': 'query success!'
        #}
        # result = sql
    return result

@handler.route("/data/queryDimension",methods=['POST'])
def query_dimension():

    current_app.logger.info('get queryDimension...........')
    if request.method == 'POST':
        data = request.get_data()
        current_app.logger.info(data)
        j = json.loads(data)
        result = dbhelper.get_data_by_concat(j['checked_quotas_sql'])

    return result
