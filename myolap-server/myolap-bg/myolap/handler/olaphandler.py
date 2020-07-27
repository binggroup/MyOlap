# -*- coding: utf-8 -*-

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify,current_app,send_file,Response,make_response
)
import json,time
from myolap.dataquery import dbhelper
from myolap.handler import json_result
from myolap.utils.funcutils import get_sql_field,get_pandas_express
from myolap.utils.const import _const

import pandas as pd

handler = Blueprint('olapconfig', __name__)

@handler.route("/olap/olap/query", methods=['POST'])
def olapconfig_query():
    #目前不支持分頁
    result = 'fail'
    code = 0
    message = '查询数据失败';
    success = False
    try:
        formdata = json.loads(request.get_data())
        #根据formdata 拼装sql
        pdresult = get_data_mysql(formdata )
        result = {
            "data": json.loads(pdresult.to_json(orient='records', date_format='iso', double_precision=2))
        }
        message ='查询数据成功'
        success = True

    except Exception as e:
        message = 'error: %s' %(e)
        current_app.logger.error('error: %s' %(e))
    return json_result(result=result, code=0, message=message,success=success)




@handler.route("/olap/olap/download", methods=['POST'])
def olapconfig_download():
    #目前不支持分頁
    formdata = json.loads(request.get_data())
    print(formdata)
    # from myolap.dataquery.dbhelper import get_data_by_dsandsql

    #根据formdata 拼装sql
    pdresult = get_data_mysql(formdata )
    #处理流下载

    from io import BytesIO
    outfile = BytesIO()
    pdresult.to_excel(outfile, sheet_name='Sheet1',columns=formdata['columns'],header=formdata['header'],index=False)
    outfile.seek(0)
    return send_file(outfile, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',as_attachment=True, attachment_filename='download.xlsx')


def get_bracket_string(items):
    #根据列表返回小括号（）包括的字符串
    str =''
    for item in items:
        str = str + "'" + item + "',"
    if len(str)>1:
        str="(" + str[0:len(str)-1] + ")"
    return str

def get_where_field(all_conditional_field):
    # 对条件进行分析，找出维度条件 和 度量条件 拼装成列表形势
    where_dim_field = []
    where_metric_field = []

    for sqlfield_key in all_conditional_field:
        print(sqlfield_key)
        obj = all_conditional_field[sqlfield_key]



        if obj['column_type'] == _const.COLUMN_TYPE_DIM:
            # 维度条件
            if obj['sql_field_type'] == _const.SQL_FIELD_TYPE_STR:
                if len(obj['value']) == 1 and obj['value'][0] =='~' :
                    pass
                else:
                    if obj['sql_field'] == 'appkey':
                        where_dim_field.append(" {}='{}' ".format(obj['sql_express'], obj['value']))
                    else:
                        where_dim_field.append(' {} in {} '.format(obj['sql_express'], get_bracket_string(obj['value'])))
            elif obj['sql_field_type'] == _const.SQL_FIELD_TYPE_DATE:
                where_dim_field.append(
                    " {} >= '{}' AND {} <= '{}'".format(obj['sql_express'], obj['from'], obj['sql_express'], obj['to']))
            elif obj['sql_field_type'] == _const.SQL_FIELD_TYPE_NUM :
                where_dim_field.append(
                    " {} >= '{}' AND {} <= '{}'".format(obj['sql_express'], obj['from'], obj['sql_express'], obj['to']))
            else:
                current_app.logger.error('未定义的数据类型:{}'.format(obj['sql_field_type']))

        elif obj['column_type'] == _const.COLUMN_TYPE_METRIC:
            # 度量条件
            if obj['sql_field_type'] == _const.SQL_FIELD_TYPE_NUM:
                if str(obj['from']).strip() != '':
                    where_metric_field.append( " {} >= {} ".format(obj['sql_field'], obj['from']))
                if str(obj['to']).strip() != '':
                    where_metric_field.append( " {} <= {} ".format(obj['sql_field'], obj['to']))
                # where_metric_field.append(
                #     " {} >= {} & {} <= {}".format( obj['sql_field'], obj['from'], obj['sql_field'], obj['to']))
            else:
                current_app.logger.error('未定义的类型:{}'.format(obj['sql_field_type']))


    print('where==============')
    print(where_dim_field)
    print('where==============')
    print(where_metric_field)
    print('where==============')

    return where_dim_field,where_metric_field

def get_data_mysql(formdata ):
    dimension_field = formdata['dimension_field']
    query_field =formdata['query_field']
    all_query_field=formdata['all_query_field']
    #条件字段合并到一个对象中  数据结构是一样的
    conditional_field=formdata['fixed_conditional_field']
    if formdata['other_conditional_field'] is not None:
        conditional_field.update(formdata['other_conditional_field'])

    #对维度列进行加工
    sql_col_dim_fields=[]
    sql_col_groupby_fields=[]
    sql_merge_keys=[]
    #求汇总或者平均数据的时候，维度dim定义为固定常数维度   方便后面dataframe合并
    # sql_avg_dim_fields =[]
    # sql_sum_dim_fields = []
    for field in dimension_field:
        sql_col_dim_fields.append(' {} as {} '.format(field['sql_express'], field['sql_field']))
        sql_col_groupby_fields.append(' {} '.format(field['sql_express']))
        sql_merge_keys.append(field['sql_field'])

    #对条件进行分析，找出维度条件 和 度量条件
    where_dim_field, where_metric_field = get_where_field(conditional_field)

    print('where==============')
    #对跨模型计算字段进行分析，找出依赖字段
    calc_field ={}
    print('calc field   ~=======')
    if query_field.__contains__('~'):
        for f in query_field['~']:
            calc_field.update(get_sql_field(f['sql_express']))

    print(calc_field)
    #从query_field中找出已经正常选中的字段，
    for qmodel in query_field:
        for field in query_field[qmodel]:
            calc_field[field['sql_field']] = 1

    #
    print('zhuijia hou....')
    print(calc_field)

    #对查询字段进行加工
    from myolap.model.sysdbmodel import OlapModelConfig, OlapModelConfigMetadata

    per = get_permission(formdata['olap_id'])

    sqls={}
    for qmodel in all_query_field:
        if qmodel =='~':
            print('qmodel==~ continue...................')
            continue

        sql_col_v_fields = []

        for field in all_query_field[qmodel]:
            #包含在calc_field 则进行计算
            if calc_field.__contains__(field['sql_field']):
                sql_col_v_fields.append(' {} as {} '.format(field['sql_express'], field['sql_field']))

        print(sql_col_v_fields)
        if len(sql_col_v_fields)> 0 :
            #长度大于0才进行计算
            u = g.session.query(OlapModelConfig).filter(OlapModelConfig.model_name == qmodel).first()
            strsql = ' SELECT '
            if len(sql_col_dim_fields)>0:
                strsql = strsql + ','.join(sql_col_dim_fields) + ','
            strsql = strsql + ','.join(sql_col_v_fields)
            strsql = strsql + ' FROM ( ' + u.model_sql + ' ) x WHERE 1=1 '
            if len( where_dim_field ) > 0:
                strsql = strsql + ' AND '  + ' AND '.join(where_dim_field)
            #行权限限制
            if len(per['row_permission']) >0:
                strsql = strsql + ' AND ' + ' AND '.join(per['row_permission'])

            if len(sql_col_groupby_fields) > 0:
                strsql = strsql + ' GROUP BY ' + ','.join(sql_col_groupby_fields)

            print('==========the sql is==============')
            print(strsql)

            df= dbhelper.get_data_by_dsandsql(u.datasource_name,  strsql)
            #加 __rowid__  用于没有groupby字段的合并
            if len(sql_merge_keys) == 0:
                #如果没有维度，则是真个记录集groupby ，出来只有一行数据 此时pandas合并的时候，需要一个mergekey
                #这里默认加一个行号作为mergekey
                df['__rowid__'] = range(1, len(df) + 1)
            sqls[qmodel] = df

    #合并数据
    if len(sql_merge_keys) > 0:
        pd_all = dbhelper.merge_dataframe(sql_merge_keys, [ df for df in sqls.values() ])
    else:
        pd_all = dbhelper.merge_dataframe(['__rowid__'], [df for df in sqls.values()])
        pass
    # pd_all_sum = dbhelper.merge_dataframe_rowid(sql_merge_keys,[ df for df in sqls_sum.values()],'合计')
    # pd_all_avg = dbhelper.merge_dataframe_rowid(sql_merge_keys,[ df for df in sqls_avg.values()],'平均')

    # 跨模型计算字段处理
    if query_field.__contains__('~'):
        for f in query_field['~']:
            pandas_express = get_pandas_express(f['sql_field'], f['sql_express'])
            print('pandas express=')
            print(pandas_express)
            # 跨字段计算
            pd_all.eval(pandas_express, inplace=True)

    # 合并后筛选维度数据
    if len(where_metric_field) > 0:
        str_where = ' & '.join(where_metric_field)
        print('where tiaojian ============')
        print(str_where)
        pd_all = pd_all.query(str_where)


    #找到所有维度字段
    all_columns = pd_all.columns
    sql_value_fields = set(pd_all.columns).difference(sql_merge_keys,['__rowid__'])

    #最后处理汇总和平均
    pd_all_sum = pd_all[sql_value_fields].sum()
    pd_all_avg = pd_all[sql_value_fields].mean()

    pd_all_sum['__rowid__'] ='合计'
    pd_all_avg['__rowid__'] = '均值'
    for col in sql_merge_keys:
        pd_all_sum[col] = '-'
        pd_all_avg[col] = '-'
    #处理不展示合计和平均的字段
    for qmodel in query_field:
        for field in query_field[qmodel]:
            #是否展示均值
            if not field['is_average']:
                pd_all_avg[field['sql_field']] ='-'
            #是否展示总计
            if not field['is_total']:
                pd_all_sum[field['sql_field']] = '-'

    pd_all = pd_all.append(pd_all_sum,ignore_index=True)
    pd_all = pd_all.append(pd_all_avg,ignore_index=True)

    #列权限限制
    if len(per['col_permission'])>0:
        set_col = set(per['col_permission'])
        for col in all_columns:
            if col =='__rowid__' or col in set_col:
                pass
            else:
                pd_all.drop(col, axis=1, inplace=True)

    # result = {
    #     "data": json.loads(pd_all.to_json(orient='records', date_format='iso', double_precision=2))
    # }
    # return json_result(result=result,code=200,message='ok')
    # 页面数据和下载数据公用查询，  返回不同类型
    return pd_all

def get_permission(olap_id):
    #根据权限设置，限制数据以及维度行权限
    result =[]

    from myolap.utils.authutils import get_current_username
    current_username = get_current_username()
    print(current_username)

    row_permission = []    #空列表，表示不做限制
    col_permission = []    #空列表，表示不做限制
    if current_username =='admin' :
        #管理员或者创建者自己，新增的时候不做限制
        pass
    else:
        # olap_id = formdata['olap_id']
        from myolap.model.sysdbmodel import OlapDimension,OlapDimensionPermission, multi_to_list_by_columns
        #查询多维表对象
        olapobj = g.session.query(OlapDimension).filter(OlapDimension.olap_id == olap_id).first()

        #db没有记录 表示多维表是新增的状态下，还没有保存到db
        if olapobj is None:
            pass
        else:
            permission = None
            #找到当前用户的权限设置
            for per in olapobj.permission:
                if per.username == current_username:
                    permission = per
                    break
            if permission is None:
                #没赋予权限
                row_permission.append(' {}  =  {} '.format(1,2))   #限制不能查看 给一个不可能==true的表达式
                # col_permission=['__rowid__']                       #限制不能查看，给一个无用的序号列
            else:
                #有记录 表示有权限，需要进一步判断行、列权限
                rowper = json.loads( permission.row_permission)
                for p in rowper:
                    if p['op'].upper() == 'EQ':
                        row_permission.append(" {} = '{}' ".format( p['sql_express'] , p['val'] ))
                    elif p['op'].upper() == 'IN':
                        row_permission.append(' {} in {} '.format(p['sql_express'], get_bracket_string(p['val'].split(','))))
                    else:
                        pass

                col_permission = json.loads( permission.col_permission)
                # col_permission.append('__rowid__')

    result ={
        'row_permission': row_permission,
        'col_permission': col_permission
    }

    #问题 ：缺少olap_id  无法获取用户权限限制

    return result

def get_dimension_items_mysql(formdata ):
    model_name = formdata['model_names']
    sql_field =formdata['sql_field'].strip()
    sql_express=formdata['sql_express'].strip()

    print('where==============')
    print(formdata)
    #对查询字段进行加工
    from myolap.model.sysdbmodel import OlapModelConfig, OlapModelConfigMetadata

    per = get_permission(formdata['olap_id'])

    keys_of_dim = {}
    list_dim = []
    for qmodel in model_name:
        print(qmodel)
        u = g.session.query(OlapModelConfig).filter(OlapModelConfig.model_name == qmodel).first()

        strsql =' SELECT DISTINCT ' + sql_express + ' AS ' + sql_field
        strsql = strsql + ' FROM ( ' + u.model_sql + ' ) x WHERE 1=1 '

        # 行权限限制
        if len(per['row_permission']) > 0:
            strsql = strsql + ' AND ' + ' AND '.join(per['row_permission'])

        print('==========the sql is==============')
        print(strsql)
        df= dbhelper.get_data_by_dsandsql(u.datasource_name,  strsql)
        for v in df[sql_field].drop_duplicates().values.tolist():
            if v not in keys_of_dim and len(v.strip()) > 0:
                keys_of_dim[v.strip()] = 1
                list_dim.append({"id":v.strip(), "name":v.strip()})

    result = list_dim
    return result

    # return json_result(result=result,code=200,message='ok')




# def get_dimension_metricdata_mysql(formdata ):
#     model_name = formdata['model_name']
#     sql_field =formdata['sql_field'].strip(' ')
#     sql_express=formdata['sql_express'].strip(' ')
#
#     print('where==============')
#     print(formdata)
#     #对查询字段进行加工
#     from myolap.model.sysdbmodel import OlapModelConfig, OlapModelConfigMetadata
#
#     keys_of_dim = {}
#
#     u = g.session.query(OlapModelConfig).filter(OlapModelConfig.model_name == model_name).first()
#
#     strsql =' SELECT MAX( ' + sql_express + ') AS ' + 'max_' + sql_field + ','
#     strsql = strsql + ' MIN( ' + sql_express +') AS min_' + sql_field
#     strsql = strsql + ' FROM ( ' + u.model_sql + ' ) x WHERE 1=1 '
#     print('==========the sql is==============')
#     print(strsql)
#     df= dbhelper.get_data_by_dsandsql(u.datasource_name,  strsql)
#     for v in df[sql_field].drop_duplicates().values.tolist():
#         keys_of_dim[v]=1
#
#         # dim_values.append(df[sql_field].drop_duplicates().values.tolist())
#     list_dim = list(keys_of_dim.keys())
#     result = {
#         "data": list_dim
#     }
#
#     return json_result(result=result,code=200,message='ok')



@handler.route("/olap/olapconfig/checkfield", methods=['POST'])
def olapconfig_checkfield():
    #检查olap多维表的字段配置是否正确

    result = 'fail'
    code = 0
    message = '检查字段失败';
    success = False
    try:
        formdata = json.loads(request.get_data())
        from myolap.model.sysdbmodel import OlapModelConfig, OlapModelConfigMetadata
        u = g.session.query(OlapModelConfig).filter(OlapModelConfig.model_name == formdata['model_name']).first()

        if u is None:
            # 校验失败 模型没找到
            message = '模型校验失败，没有找到模型'
        else:
            #提交请求到对应数据源，查看是否执行成功
            sql = 'select {} from ( {} limit 1 ) x '.format(formdata['sql_express'], u.model_sql)

            from myolap.dataquery.dbhelper import get_data_by_dsandsql
            r = dbhelper.get_data_by_dsandsql(u.datasource_name,sql)
            if r is not None:
                code = 200
                message='校验成功'
                result ='ok'
                success = True
            else:
                message = '模型校验失败'

    except Exception as e:
        message = 'error: %s' %(e)
        current_app.logger.error('error: %s' %(e))
    return json_result(result=result, code=0, message=message,success=success)






@handler.route("/olap/olapconfig/querydimension", methods=['POST'])
def olapconfig_querydimension():
    result = 'fail'
    code = 0
    message = '查询维度信息失败';
    success = False
    try:
        formdata = json.loads(request.get_data())
        print(formdata)
        result = get_dimension_items_mysql(formdata)
        message = '查询维度信息成功';
        success = True
    except Exception as e:
        message = 'error: %s' %(e)
        current_app.logger.error('error: %s' %(e))
    return json_result(result=result, code=0, message=message,success=success)
    # return result


# @handler.route("/olap/olapconfig/querymetric", methods=['POST'])
# def olapconfig_querymetric():
#     formdata = json.loads(request.get_data())
#     print(formdata)
#     result = get_dimension_metricdata_mysql(formdata)
#
#     return result


@handler.route("/olap/olapconfig/save", methods=['POST'])
def olapconfig_save():
    #检查olap多维表的字段配置是否正确
    result = 'fail'
    code = 0
    message = '保存多维表信息失败';
    success = False
    try:
        from myolap.utils.authutils import get_current_username
        from myolap.model.sysdbmodel import OlapDimension
        username = get_current_username()
        formdata = json.loads(request.get_data())

        u = g.session.query(OlapDimension).filter(OlapDimension.olap_id == formdata['olap_id']).first()
        if u is None:
            # 新增
            u = OlapDimension()
            u.olap_id = formdata['olap_id']
            g.session.add(u)

        #更新字段内容
        u.dimension_name = formdata['dimension_name']
        u.create_by = username
        u.version = formdata['version']
        str_checked_list = json.dumps(formdata['checked_list'])
        str_filter_list = json.dumps(formdata['filter_list'])

        u.checked_list = str_checked_list
        u.filter_list = str_filter_list
        g.session.commit()
        result ='ok'
        message ='保存多维表信息成功'
        success = True
    except Exception as e:
        message = 'error: %s' %(e)
        current_app.logger.error('error: %s' %(e))
    return json_result(result=result, code=0, message=message,success=success)




@handler.route("/olap/olapconfig/shortcut/save", methods=['POST'])
def olapconfig_shortcut_save():
    #检查olap多维表的字段配置是否正确
    result = 'fail'
    code = 0
    message = '保存快捷键信息失败';
    success = False
    try:
        from myolap.utils.authutils import get_current_username
        from myolap.model.sysdbmodel import OlapDimensionShortcut
        username = get_current_username()
        formdata = json.loads(request.get_data())
        u = g.session.query(OlapDimensionShortcut).filter(OlapDimensionShortcut.id == formdata['shortcut_id']).first()
        if u is None:
            # 新增
            u = OlapDimensionShortcut()
            u.id = formdata['shortcut_id']
            g.session.add(u)
        #更新字段内容
        u.shortcut_name = formdata['shortcut_name']
        u.olap_id = formdata['olap_id']
        u.create_by = username
        u.version = formdata['version']
        str_checked_list = json.dumps(formdata['checked_list'])
        str_filter_list = json.dumps(formdata['filter_list'])

        u.checked_list = str_checked_list
        u.filter_list = str_filter_list

        g.session.commit()
        result ='ok'
        message ='保存快捷键信息成功'
        success = True

    except Exception as e:
        message = 'error: %s' %(e)
        current_app.logger.error('error: %s' %(e))
    return json_result(result=result, code=0, message=message,success=success)



@handler.route("/olap/olapconfig/get", methods=['GET'])
def olapconfig_get():
    # 检查olap多维表的字段配置是否正确
    result = 'fail'
    code = 0
    message = '获取多维表信息失败';
    success = False
    try:
        olap_id = request.args.get("olap_id")
        per = get_permission(olap_id)
        from myolap.model.sysdbmodel import OlapDimension
        u = g.session.query(OlapDimension).filter(OlapDimension.olap_id == olap_id).first()

        if u is None:
            result = {
                "checked_list": [],
                "filter_list": {},
                "dimension_name": '',
                "olap_id": olap_id
            }
            message = '未查询到相关信息'
            success = True
        else:
            #进行列限制
            allow_cols =per['col_permission']
            checked_list = json.loads(u.checked_list)
            filter_list = json.loads(u.filter_list)
            remove_not_allow_field(allow_cols,checked_list,filter_list)

            result = {
                "checked_list": checked_list,
                "dimension_name":u.dimension_name,
                "filter_list": filter_list,
                "olap_id": u.olap_id
            }
            message = '查询信息成功'
            success = True
    except Exception as e:
        message = 'error: %s' %(e)
        current_app.logger.error('error: %s' %(e))
    return json_result(result=result, code=0, message=message,success=success)



def remove_not_allow_field(allow_cols, checked_list,filter_list):
    if len(allow_cols) > 0:
        for item in checked_list:
            for child in item['children'][:: -1]:
                if child['sql_field'] == '__rowid__' or child['sql_field'] in allow_cols:
                    pass
                else:
                    # 不在允许的列范围内
                    item['children'].remove(child)

        for child in filter_list['add_no_must_filter_list'][:: -1]:
            if  child['sql_field'] == '__rowid__' or child['sql_field'] in allow_cols:
                pass
            else:
                # 不在允许的列范围内
                filter_list['add_no_must_filter_list'].remove(child)

        for child in filter_list['no_must_filter_list'][:: -1]:
            print('====================no_must_filter_list')
            print(child['sql_field'])
            if  child['sql_field'] == '__rowid__' or child['sql_field'] in allow_cols:
                pass
            else:
                # 不在允许的列范围内
                filter_list['no_must_filter_list'].remove(child)
                print('yichu............')
                print(child['sql_field'])

        for child in filter_list['must_filter_list'][:: -1]:
            if  child['sql_field'] == '__rowid__' or child['sql_field'] in allow_cols:
                pass
            else:
                # 不在允许的列范围内
                filter_list['must_filter_list'].remove(child)
    else:
        pass

@handler.route("/olap/olapconfig/shortcut/get", methods=['GET'])
def olapconfig_shortcut_get():
    # 检查olap多维表的字段配置是否正确
    result = 'fail'
    code = 0
    message = '获取快捷键信息失败';
    success = False
    try:
        shortcut_id = request.args.get("shortcut_id")
        from myolap.model.sysdbmodel import OlapDimensionShortcut
        u = g.session.query(OlapDimensionShortcut).filter(OlapDimensionShortcut.id == shortcut_id).first()

        if u is None:
            result = {
                "checked_list": [],
                "filter_list": {},
                "shortcut_name": '',
                "olap_id": '',
                "shortcut_id":''
            }
            message = '未查询到快捷键信息'
            success = True
        else:
            result = {
                "checked_list": u.checked_list,
                "shortcut_name":u.shortcut_name,
                "filter_list":u.filter_list,
                "olap_id": u.olap_id,
                "shortcut_id":u.id
            }
            message = '查询信息成功'
            success = True
    except Exception as e:
        message = 'error: %s' %(e)
        current_app.logger.error('error: %s' %(e))
    return json_result(result=result, code=0, message=message,success=success)


@handler.route("/olap/olapconfig/list", methods=['GET'])
def olapconfig_list():
    # 检查olap多维表的字段配置是否正确

    result = 'fail'
    code = 0
    message = '获取快捷键信息失败';
    success = False
    try:
        from myolap.utils.authutils import get_current_username
        #当前登录用户
        username = get_current_username()
        from myolap.model.sysdbmodel import OlapDimension,OlapDimensionPermission, multi_to_list, multi_to_list_by_columns2
        # 只查询指定的字段
        # create_by = request.args.get("create_by")
        if username == 'admin':
            print('admin........')
            modellist = g.session.query(OlapDimension).all()
        else:
            print('普通用户')
            modellist = g.session.query(OlapDimension).filter(OlapDimension.create_by == username).all()

        list = multi_to_list_by_columns2(modellist,['olap_id','dimension_name','create_by'],'permission')
        result = {
            "current": 0,
            "pages": 0,
            "records": list,
            "size": 0,
            "total": 0
        }
        message = '查询信息成功'
        success = True
    except Exception as e:
        message = 'error: %s' %(e)
        current_app.logger.error('error: %s' %(e))
    return json_result(result=result, code=0, message=message,success=success)





@handler.route("/olap/olapconfig/shortcut/list", methods=['GET'])
def olapconfig_shortcut_list():
    # 检查olap多维表的字段配置是否正确

    result = 'fail'
    code = 0
    message = '获取快捷键信息失败';
    success = False
    try:

        from myolap.utils.authutils import get_current_username
        username = get_current_username()
        olap_id = request.args.get("olap_id")

        from myolap.model.sysdbmodel import OlapDimensionShortcut, multi_to_list, multi_to_list_by_columns

        modellist = g.session.query(OlapDimensionShortcut)\
            .with_entities(OlapDimensionShortcut.id,OlapDimensionShortcut.olap_id,OlapDimensionShortcut.shortcut_name)\
            .filter(OlapDimensionShortcut.create_by == username).filter(OlapDimensionShortcut.olap_id == olap_id).all()

        list = multi_to_list_by_columns(modellist,['id','olap_id','shortcut_name'])
        result = {
            "current": 0,
            "pages": 0,
            "records": list,
            "size": 0,
            "total": 0
        }
        message = '查询信息成功'
        success = True
    except Exception as e:
        message = 'error: %s' % (e)
        current_app.logger.error('error: %s' % (e))
    return json_result(result=result, code=0, message=message, success=success)



@handler.route("/olap/olapconfig/delete", methods=['DELETE'])
def olapconfig_delete():
    # 删除某张多维表
    result = 'fail'
    code = 0
    message = '获取快捷键信息失败';
    success = False
    try:
        olap_id = request.args.get("id")
        print('delete................')
        print(olap_id)

        # from myolap.app import sysdb
        from myolap.model.sysdbmodel import OlapDimension
        g.session.query(OlapDimension).filter(OlapDimension.olap_id == olap_id).delete()
        g.session.commit()
        result ='OK'
        message = '删除成功'
        success = True

    except Exception as e:
        message = 'error: %s' % (e)
        current_app.logger.error('error: %s' % (e))
    return json_result(result=result, code=0, message=message, success=success)


@handler.route("/olap/olapconfig/shortcut/delete", methods=['DELETE'])
def olapconfig_shortcut_delete():
    #删除某个快捷键
    result = 'fail'
    code = 0
    message = '删除信息失败';
    success = False
    try:
        shortcut_id = request.args.get("shortcut_id")
        from myolap.model.sysdbmodel import OlapDimensionShortcut
        g.session.query(OlapDimensionShortcut).filter(OlapDimensionShortcut.id==shortcut_id).delete()
        g.session.commit()
        result = 'OK'
        message ='删除数据成功'
        success = True
    except Exception as e:
        message = 'error: %s' % (e)
        current_app.logger.error('error: %s' % (e))
    return json_result(result=result, code=0, message=message, success=success)
