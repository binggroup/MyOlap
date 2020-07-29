# -*- coding: utf-8 -*-

from flask import current_app, g
from flask.cli import with_appcontext
import pymysql
import pandas as pd
# from DBUtils.PooledDB import PooledDB
from myolap.dataquery import dbpool
# from celery import Celery
from myolap.config import usingconfig
import time
import json

from myolap.dataquery.dbtasks import celery,get_data_onesql,get_data_test

from concurrent.futures import ThreadPoolExecutor,as_completed
# celery = Celery('myolap', broker=usingconfig.CELERY_BROKER_URL, backend=usingconfig.CELERY_RESULT_BACKEND)



# def get_db():
#     current_app.logger.info('.........dbhelper....get db connect......')
#     if 'SYS_DB_POOL' not in g:
#         g.SYS_DB_POOL =dbpool.SysDbPool.SYS_DB_POOL.connection()
#     return g.SYS_DB_POOL


def close_db(e=None):
    db = g.pop('SYS_DB_POOL', None)
    current_app.logger.info('.........dbhelper....close db...')

    if db is not None:
        db.close()


def init_app(app):
    app.teardown_appcontext(close_db)
    # app.cli.add_command(init_db_command)


# def init_db():
#     db = get_db()
#     print('init db')
#     # with current_app.open_resource('schema.sql') as f:
#     #     db.executescript(f.read().decode('utf8'))
#
#
#
#
# @with_appcontext
# def init_db_command():
#     """Clear the existing data and create new tables."""
#     init_db()
#     print('init db command.....')

# @celery.task
# def get_data_onesql(sql,sec):
#     # db = get_db()
#     current_app.logger.info('.........开始查询...' + str(sec) )
#     current_app.logger.info(sql)
#     # df = pd.read_sql(sql=sql, con=db)  # read data to DataFrame 'df
#     # with app.app_context():
#     #     print('app.........************')
#     time.sleep(sec)
#     #     print('app.........************')
#     #     app.logger.info('.........查询结束...')
#
#     return 'result=====' + sql
#=================================================================================

def test_thread_add(app,n1,n2):
    with app.app_context():
        v = n1 + n2
        import threading
        time.sleep(n1)
        print('==============db=============')
        # db = get_db()
        test =get_data_test('adb');
        test='aaaaa'
        print(test)
        # print(db)
        print('==============db=============')
        print('test_thread_add :', v , ', tid:',threading.currentThread().ident)


    return v

def test_thread():

    from myolap.app import executor,app

    f12= executor.submit(test_thread_add, app,1, 2)
    f56= executor.submit(test_thread_add, app,5, 6)
    f34 = executor.submit(test_thread_add, app, 3, 4)

    for future in as_completed([f12,f34,f56]):  # as_completed()接受一个可迭代的Future序列,返回一个生成器,在完成或异常时返回这个Future对象
        print('一个任务完成.')
        print(future)
        print(future.result())

    return 'ok'

#多线程实现
# def get_data_onesql(sql,sec):
#     db = None
#     r =''
#     df = None
#     try:
#         db = get_db()
#         df = pd.read_sql(sql=sql, con=db)
#         time.sleep(sec)
#         print(sql)
#         r = 'ok'
#         print(df.to_json())
#     except Exception as e:
#         print('error:' )
#         print(e)
#     finally:
#         if db:
#             close_db()
#
#     return r + '=======' + sql
#     # return df.to_json()
#
# def get_data(checked_quotas_sql):
#     i = 10
#     r = []
#     # 提交任务
#
#     executor = ThreadPoolExecutor(max_workers=5)
#
#     for item in checked_quotas_sql:
#         i = i - 1
#         current_app.logger.info(item.get('dsname'))
#
#         str_key = item.get('dsname')
#         str_sql = item.get('sql')
#         current_app.logger.info('=================')
#         current_app.logger.info(str_key)
#         current_app.logger.info(str_sql)
#         current_app.logger.info('=================')
#
#         # result = current_app.executor.submit(current_app, get_data_onesql,str_sql, i * 10)
#         result = executor.submit(current_app, get_data_onesql, str_sql, i * 10)
#
#         # result = get_data_onesql.delay(str_sql, i*1)
#         r.append(result)
#     #等待多个任务完成
#
#     current_app.logger.info('waiting for result.................')
#     for future in as_completed(r):
#         data = future.result()
#         print("in main: get page {}s success".format(data))
#
#     # for result in r:
#     #     while not result.ready():
#     #         pass
#     #     current_app.logger.info('=================CHAXUN JIEGUO.........')
#     #     current_app.logger.info(result)
#
#     return 'ok'

def get_tempdata(datasource):
    r = get_data_test.delay(datasource)
    while not r.ready():
        pass
    current_app.logger.info('=============等待结果........')
    json_result = r.result
    return json_result



#=================================================================================
# def get_datasource(ds):
#     r = get_data_test.delay('adb')
#     print('delay......')
#     while not r.ready():
#         pass
#     current_app.logger.info('=================CHAXUN JIEGUO.........')
#     json_result = r.result
#     return json_result

def get_data_by_dsandsql(datasource,sql):
    r = get_data_onesql(datasource,sql)
    return r

def get_meta_by_dsandsql(datasource,sql):
    #获取数据以及元数据
    db = None
    meta, df = None,None
    try:
        from myolap.dataquery.dbtasks import get_db
        db = get_db(datasource)
        print('exe sql=')
        print(sql)

        cursor = db.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()

        meta = cursor.description
        # 执行结果转化为dataframe
        df = pd.DataFrame(list(result))
        # df = pd.read_sql(sql=sql, con=db)

        print(df.to_json())
    except Exception as e:
        print('error:' )
        print(e)
    finally:
        print('==============close db...zuihouhhhhhhhhhhhhhhhhhhhh')
        close_db(db)

    return meta,df


#celery 实现
def get_data(checked_quotas_sql,check_dimension):
    rlist = []
    pd_result = []
    result = ''
    # 提交任务
    for item in checked_quotas_sql:
        current_app.logger.info(item.get('dsname'))

        str_key = item.get('dsname')
        str_sql = item.get('sql')
        str_datasource = item.get('datasource')
        current_app.logger.info('=================')
        current_app.logger.info(str_key)
        current_app.logger.info(str_sql)
        current_app.logger.info(str_datasource)
        current_app.logger.info('=================')

        #后台进程查询
        #result = get_data_onesql.delay(str_datasource,str_sql)
        result = get_data_onesql(str_datasource, str_sql)
        pd_result.append(result)
        # rlist.append(result)
    #等待多个任务完成


    # for r in rlist:
        #等待后来celery查询结果
        # while not r.ready():
        #     pass
        # current_app.logger.info('=================CHAXUN JIEGUO.........')
        # json_result = r.result
        # current_app.logger.info(json_result)
        # df = pd.read_json(json_result)
        # pd_result.append(df)

    # 合并
    joinkey =[]
    for d in check_dimension:
        joinkey.append(d.get('field_name'))

    pd_all = pd_result[0]
    if(len(pd_result)) >= 2:
        pd0 = pd_result[0]
        pd1 = pd_result[1]

        pd_all = pd.merge(pd_result[0], pd_result[1], how='outer', on=joinkey)
        #循环merge多个数据集合
        for i in range(2,len(pd_result)):
            pd_all = pd.merge(pd_all,pd_result[i], how='outer', on=joinkey)
    #加一个行号 __rowid__
    pd_all['__rowid__'] = range(1,len(pd_all) + 1)

    return pd_all.to_json(orient='records',date_format='R')


def merge_dataframe(merge_key, pd_result):

    if (len(pd_result)) >= 2:
        pd0 = pd_result[0]
        pd1 = pd_result[1]

        pd_all = pd.merge(pd_result[0], pd_result[1], how='outer', on=merge_key)
        # 循环merge多个数据集合
        for i in range(2, len(pd_result)):
            pd_all = pd.merge(pd_all, pd_result[i], how='outer', on=merge_key)
    else:
        pd_all = pd_result[0]
    # 加一个行号 __rowid__
    pd_all['__rowid__'] = range(1, len(pd_all) + 1)
    return pd_all



# def merge_dataframe_rowid(merge_key, pd_result,rowid):
#
#     if (len(pd_result)) >= 2:
#         pd0 = pd_result[0]
#         pd1 = pd_result[1]
#
#         pd_all = pd.merge(pd_result[0], pd_result[1], how='outer', on=merge_key)
#         # 循环merge多个数据集合
#         for i in range(2, len(pd_result)):
#             pd_all = pd.merge(pd_all, pd_result[i], how='outer', on=merge_key)
#     else:
#         pd_all = pd_result[0]
#     # 加一个行号 __rowid__
#     pd_all['__rowid__'] = rowid
#     return pd_all


#查询维度明细数据接口
def get_data_by_concat(checked_quotas_sql):
    rlist = []
    pd_result = []
    result = ''
    # 提交任务
    for item in checked_quotas_sql:
        current_app.logger.info(item.get('dsname'))

        str_key = item.get('dsname')
        str_sql = item.get('sql')
        str_datasource = item.get('datasource')
        current_app.logger.info('=================')
        current_app.logger.info(str_key)
        current_app.logger.info(str_sql)
        current_app.logger.info(str_datasource)
        current_app.logger.info('=================')

        #后台进程查询
        #result = get_data_onesql.delay(str_datasource,str_sql)
        result = get_data_onesql(str_datasource, str_sql)
        pd_result.append(result)
        # rlist.append(result)
    #等待多个任务完成


    # for r in rlist:
        #等待后来celery查询结果
        # while not r.ready():
        #     pass
        # current_app.logger.info('=================CHAXUN JIEGUO.........')
        # json_result = r.result
        # current_app.logger.info(json_result)
        # df = pd.read_json(json_result)
        # pd_result.append(df)

    pd_all = pd_result[0]
    if(len(pd_result)) >= 2:
        pd0 = pd_result[0]
        pd1 = pd_result[1]
        pd_all = pd.concat([pd_result[0], pd_result[1]], axis=0, join='outer')
        #循环merge多个数据集合
        for i in range(2,len(pd_result)):
            pd_all = pd.concat([pd_all, pd_result[i]], axis=0, join='outer')

    #去除重复项，index重新编号
    pd_all = pd_all.drop_duplicates().reset_index(drop='true')
    pd_all = pd_all.dropna()
    return pd_all.to_json(orient='records', date_format='iso')
