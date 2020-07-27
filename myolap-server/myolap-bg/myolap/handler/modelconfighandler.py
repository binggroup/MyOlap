# -*- coding: utf-8 -*-

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify,current_app
)
import json,time
from myolap.dataquery import dbhelper
from myolap.handler import json_result


handler = Blueprint('modelconfig', __name__)

#========================未用到，暂时注释掉
# @handler.route("/olap/modelconfig/get")
# def dimension_get():
#     from myolap.model.sysdbmodel import OlapModelConfig
#     u = OlapModelConfig.query.filter_by(model_name='hooh_1').first()
#     print('ok.........')
#     print(u)
#
#     data = {
#         "code": 0,
#         "message": "",
#         "result": {
#             "model_name": u.model_name,
#             "test":u.model_sql
#         },
#         "success": True,
#         "timestamp": 0
#     }
#     return data

@handler.route("/olap/modelconfig/list", methods=['GET'])
def modelconfig_list():
    #目前不支持分頁
    # pageNo = request.args.get("pageNo")
    # pageSize = request.args.get("pageSize")

    result = 'fail'
    code = 0
    message = '获取列表失败';
    success = False

    from myolap.app import sysdb
    from myolap.model.sysdbmodel import OlapModelConfig, multi_to_list
    try:
        modellist = g.session.query(OlapModelConfig).all()
        list = multi_to_list(modellist)
        result = {
            "current": 0,
            "pages": 0,
            "records": list,
            "size": 0,
            "total": 0
        }
        success= True
        message = '获取列表成功'
    except Exception as e:
        message = 'error: %s' %(e)
        current_app.logger.error('error: %s' %(e))

    return json_result(result=result, code=0, message=message,success=success)

@handler.route("/olap/modelconfig/delete", methods=['DELETE'])
def modelconfig_delete():
    result = 'fail'
    code = 0
    message = '删除信息失败';
    success = False

    id = request.args.get("id")
    try:
        from myolap.model.sysdbmodel import OlapModelConfig,OlapModelConfigMetadata
        g.session.query(OlapModelConfigMetadata).filter(OlapModelConfigMetadata.pid == id).delete()
        g.session.query(OlapModelConfig).filter(OlapModelConfig.id==id).delete()
        g.session.commit();
        result = 'ok'
        message='删除数据成功'
        success= True
    except Exception as e:
        message = 'error: %s' %(e)
        current_app.logger.error('error: %s' %(e))
    return json_result(result=result, code=0, message=message,success=success)





@handler.route("/olap/modelconfig/preview", methods=['POST'])
def modelconfig_preview():
    """
    参数json字符串格式为：
    {
    "datasource_name": "adb",
    "model_name": "ad_dianji_01",
    "model_sql": "",
    "page_size": 10,
    "sql": "",
    "type": 0
    }

    :return:
    返回结果外层和其他统一，内部一个data，表示查询的数据列；另外一个metadata，是各个列的元数据
    {
    "code": 200,
    "message": "查询数据成功",
    "result": {
        "data": [
            {
                "adagent": "耀广",
                "adclicks": 6,
                "adexposurecnt": 149,
                "adnetname": "头条天",
                "appkey": "1514446452050",
                "cost": 0.47,
                "devicetype": "2",
                "dt": "2019-08-30",
                "spreadname": "AND天头条041"
            }

        ],
        "metadata": [
            {
                "columnAlias": "devicetype",
                "columnType": 0,
                "modelId": 0,
                "modelName": "ad_dianji_01",
                "sqlField": "devicetype",
                "sqlFieldType": "字符串"
            },
            {
                "columnAlias": "cost",
                "columnType": 2,
                "modelId": 0,
                "modelName": "ad_dianji_01",
                "sqlField": "cost",
                "sqlFieldType": "数值"
            }
        ]
    },
    "success": true,
    "timestamp": 1591262086161
    }
    """

    #pymysql 返回字段类型编码值
    # DECIMAL = 0
    # TINY = 1
    # SHORT = 2
    # LONG = 3
    # FLOAT = 4
    # DOUBLE = 5
    # NULL = 6
    # TIMESTAMP = 7
    # LONGLONG = 8
    # INT24 = 9
    # DATE = 10
    # TIME = 11
    # DATETIME = 12
    # YEAR = 13
    # NEWDATE = 14
    # VARCHAR = 15
    # BIT = 16
    # JSON = 245
    # NEWDECIMAL = 246
    # ENUM = 247
    # SET = 248
    # TINY_BLOB = 249
    # MEDIUM_BLOB = 250
    # LONG_BLOB = 251
    # BLOB = 252
    # VAR_STRING = 253
    # STRING = 254
    # GEOMETRY = 255

    result = 'fail'
    code = 0
    message = '预览数据失败';
    success = False
    try:
        formdata = json.loads(request.get_data())
        from myolap.dataquery.dbhelper import get_meta_by_dsandsql

        sql = ' {} limit 10 '.format(formdata['model_sql'])
        # 修改 通过pymysql cusor 获取元数据
        # df = get_data_by_dsandsql(formdata['datasource_name'], sql )
        meta, df = get_meta_by_dsandsql(formdata['datasource_name'], sql)
        from pymysql.constants import FIELD_TYPE
        from myolap.utils.const import _const

        metalist = []
        for m in meta:
            str_field_type= _const.SQL_FIELD_TYPE_STR
            if m[1] == FIELD_TYPE.DATE or m[1] ==FIELD_TYPE.DATETIME or m[1] ==FIELD_TYPE.NEWDATE :
                str_field_type= _const.SQL_FIELD_TYPE_DATE
            elif m[1] <= 9:
                str_field_type = _const.SQL_FIELD_TYPE_NUM
            else:
                pass

            metadata = {}
            metadata['model_id'] = 0;
            metadata['model_name'] = formdata['model_name'];
            metadata['sql_field'] = m[0];
            metadata['sql_field_type'] =str_field_type;
            metalist.append(metadata)
        print(metalist)
        result = {
            "data": json.loads(df.to_json(orient='records', date_format='iso')),
            "metadata": metalist
        }
        message ='预览数据成功'
        success = True

    except Exception as e:
        message = 'error: %s' %(e)
        current_app.logger.error('error: %s' %(e))
    return json_result(result=result, code=0, message=message,success=success)












@handler.route("/olap/modelconfig/save", methods=['POST'])
def modelconfig_save():
    """
    参数json字符串格式为：
{
    "datasource_name": "mysqltest",
    "db_type": "mysql",
    "id": 26,
    "metadata": [
        {
            "column_alias": "gamechannel",
            "column_type": 0,
            "model_id": 0,
            "model_name": "hooh_1",
            "sql_field": "gamechannel",
            "sql_field_ype": "字符串"
        },
        {
            "column_alias": "serverid",
            "column_type": 0,
            "model_id": 0,
            "model_name": "hooh_1",
            "sqlFieldType": "字符串",
            "sql_field": "serverid"
        },
        {
            "column_alias": "dcnt",
            "column_type": 2,
            "model_id": 0,
            "model_name": "hooh_1",
            "sql_field": "dcnt",
            "sql_field_ype": "数值"
        }
    ],
    "model_name": "hooh_1",
    "model_sql": "SELECT gamechannel,serverid,COUNT(DISTINCT deviceid) AS dcnt FROM h1_first_login WHERE serverid IN ('3990','1301') GROUP BY gamechannel,serverid ",
    "type": 0
}

    :return:
    返回结果


    """
    result = 'fail'
    code = 0
    message = '保存数据失败';
    success = False
    try:
        print(request.get_data())
        formdata = json.loads(request.get_data())
        from myolap.model.sysdbmodel import OlapModelConfig,OlapModelConfigMetadata

        id = formdata['id']
        u = g.session.query(OlapModelConfig).filter(OlapModelConfig.id == id).first()
        if u is None:
            #新增
            u = OlapModelConfig()
            g.session.add(u)
        else:
            #删除原来数据
            for m in u.meta_data:
                g.session.delete(m)
        #更新字段内容
        u.model_name = formdata['model_name']
        u.datasource_name = formdata['datasource_name']
        u.db_type = formdata['db_type']
        u.model_sql = formdata['model_sql']
        g.session.commit()
        u.meta_data =[]

        for meta in formdata['metadata']:
            obj = OlapModelConfigMetadata()
            obj.sql_field = meta['sql_field']
            obj.sql_field_type = meta['sql_field_type']
            obj.pid = u.id
            g.session.add(obj)
        g.session.commit()

        result = 'ok'
        message ='保存信息成功'
        success=True
    except Exception as e:
        message = 'error: %s' %(e)
        current_app.logger.error('error: %s' %(e))
    return json_result(result=result, code=0, message=message,success=success)









# @handler.route("/olap/modelconfig/metadata", methods=['GET'])
# def modelconfig_metadata():
#     """
#     参数json字符串格式为：
#     {
#     }
#
#     :return:
#     返回结果外层和其他统一，内部一个data，表示查询的数据列；另外一个metadata，是各个列的元数据
#     {
#     "code": 200,
#     "message": "查询数据成功",
#     "result": [
#         {
#             "datasource_name": "datasource_name",
#             "db_type": "db_type",
#             "metadata": [
#                 {
#                     "column_alias": "devicetype",
#                     "column_type": 0,
#                     "model_id": 0,
#                     "model_name": "ad_dianji_01",
#                     "sql_field": "devicetype",
#                     "sql_field_type": "字符串"
#                 },
#                 {
#                     "column_alias": "cost",
#                     "column_type": 2,
#                     "model_id": 0,
#                     "model_name": "ad_dianji_01",
#                     "sql_field": "cost",
#                     "sql_field_type": "数值"
#                 }
#             ],
#             "model_name": "aaa",
#             "model_sql": "model_sql"
#         }
#     ],
#     "success": true,
#     "timestamp": 1591262086161
#     }
#
#     """
#     from myolap.app import sysdb
#     from myolap.model.sysdbmodel import OlapModelConfig, OlapModelConfigMetadata, multi_to_list, single_to_dict
#
#     modellist = sysdb.session.query(OlapModelConfig).all()
#     resultlist={}
#     for model in modellist:
#         smodel = single_to_dict(model)
#
#         metalist = multi_to_list(model.meta_data)
#         smodel["meta_data"] =metalist
#         resultlist.append(smodel)
#
#     result = resultlist
#
#     return  json_result(result,code=0,message='查询成功')




@handler.route("/olap/modelconfig/metadata", methods=['GET'])
def modelconfig_metadata():
    """
    参数json字符串格式为：
    {
    }

    :return:
    返回结果外层和其他统一，内部一个data，表示查询的数据列；另外一个metadata，是各个列的元数据
    {
    "code": 200,
    "message": "查询数据成功",
    "result": [
        {
            "datasource_name": "datasource_name",
            "db_type": "db_type",
            "metadata": [
                {
                    "column_alias": "devicetype",
                    "column_type": 0,
                    "model_id": 0,
                    "model_name": "ad_dianji_01",
                    "sql_field": "devicetype",
                    "sql_field_type": "字符串"
                },
                {
                    "column_alias": "cost",
                    "column_type": 2,
                    "model_id": 0,
                    "model_name": "ad_dianji_01",
                    "sql_field": "cost",
                    "sql_field_type": "数值"
                }
            ],
            "model_name": "aaa",
            "model_sql": "model_sql"
        }
    ],
    "success": true,
    "timestamp": 1591262086161
    }

    """
    # from myolap.app import sysdb
    from myolap.model.sysdbmodel import OlapModelConfig, OlapModelConfigMetadata, multi_to_list, single_to_dict
    resultlist = {}

    modellist = g.session.query(OlapModelConfig).all()

    for model in modellist:
        smodel = single_to_dict(model)
        metalist=[]
        for meta in model.meta_data:
            metadict = single_to_dict(meta)
            metadict['model_name'] = model.model_name
            metadict['datasource_name'] = model.datasource_name
            metadict['db_type'] = model.db_type
            # metadict['model_sql'] = model.model_sql
            metalist.append(metadict)
        smodel["meta_data"] =metalist
        resultlist[model.model_name]= metalist

    result = resultlist

    return  json_result(result,code=0,message='查询成功')