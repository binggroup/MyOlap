# -*- coding: utf-8 -*-

from flask import current_app, g
# from flask.cli import with_appcontext
import pymysql
import time
import pandas as pd
from DBUtils.PooledDB import PooledDB
from myolap.dataquery import dbpool
from celery import Celery
from myolap.config import usingconfig
#
celery = Celery('myolap.dataquery.dbtasks', broker=usingconfig.CELERY_BROKER_URL, backend=usingconfig.CELERY_RESULT_BACKEND)

def get_sysdb():
    return dbpool.SysDbPool.SYS_DB_POOL.connection()
    # if 'SYS_DB_POOL' not in g:
    #     g.SYS_DB_POOL =dbpool.SysDbPool.SYS_DB_POOL.connection()
    # return g.SYS_DB_POOL

def get_db(datasource):
    # global_datasource = current_app['DATASOURCE_POOL']
    print('==============================111111111111111')
    print(current_app.datasource_pool)
    if datasource in current_app.datasource_pool:
        #初始化
        pool = current_app.datasource_pool[datasource]
        print('从连接池中去............................')
        return pool.connection()
    else:
        from myolap.model.sysdbmodel import SysDataSource
        u = SysDataSource.query.filter_by(code=datasource).first()
        if(u.db_driver == 'com.mysql.jdbc.Driver'):
            #连接mysql
            pool = PooledDB(
                creator=pymysql,  # 使用链接数据库的模块
                maxconnections=2,  # 连接池允许的最大连接数，0和None表示不限制连接数
                mincached=1,  # 初始化时，链接池中至少创建的空闲的链接，0表示不创建
                maxcached=5,  # 链接池中最多闲置的链接，0和None不限制
                maxshared=3,
                # 链接池中最多共享的链接数量，0和None表示全部共享。PS: 无用，因为pymysql和MySQLdb等模块的 threadsafety都为1，所有值无论设置为多少，_maxcached永远为0，所以永远是所有链接都共享。
                blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
                maxusage=None,  # 一个链接最多被重复使用的次数，None表示无限制
                setsession=[],  # 开始会话前执行的命令列表。如：["set datestyle to ...", "set time zone ..."]
                ping=0,
                # ping MySQL服务端，检查是否服务可用。# 如：0 = None = never, 1 = default = whenever it is requested, 2 = when a cursor is created, 4 = when a query is executed, 7 = always

                host=u.db_host,
                port=u.db_port,
                user=u.db_username,
                password=u.db_password,
                database=u.db_database,
                charset='utf8'
            )
            current_app.datasource_pool[datasource] = pool
            print('get_db。。。。加入到连接池。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。')
            print(u.db_host)
            print('===============get db ok')
            return pool.connection()
        else:
            return None

def printlog():
    current_app.logger.info('print log..........................')

def close_db(db):
    # current_app.logger.info('close dbbbbbbbbbbbbbbbb')
    if db:
        db.close()
        # current_app.logger.info('close aaaaaaaa')


def close_sysdb(e=None):
    dbpool.SysDbPool.SYS_DB_POOL.connection().close()
    # db = g.pop('SYS_DB_POOL', None)
    # if db is not None:
    #     db.close()


# def init_app(app):
#     app.teardown_appcontext(close_db)

#测试
# @celery.task
def get_data_test(datasource):
    print('begin celery get-data-test......')
    print('sleep')
    from myolap.model.sysdbmodel import SysDataSource
    u = SysDataSource.query.filter_by(code=datasource).first()
    print(u.code)
    print('=============get_data_test==================end')
    return u.db_driver

#实现一次请求多个sql并行查询
@celery.task
def get_data_onesql(datasource, sql):
    # db = get_db()
    # current_app.logger.info('.........开始查询...')
    # df = pd.read_sql(sql=sql, con=db)  # read data to DataFrame 'df
    # current_app.logger.info('.........查询结束...')
    db = None
    df = None
    try:
        # db = get_db()
        db = get_db(datasource)
        print('exe sql=')
        print(sql)

        df = pd.read_sql(sql=sql, con=db)

        print(df.to_json())
    except Exception as e:
        print('error:' )
        print(e)
    finally:
        print('==============close db...zuihouhhhhhhhhhhhhhhhhhhhh')
        close_db(db)

    # return r + '=======' + sql

    # return df.to_json()
    # 先返回dataframe对象
    return df

# def get_data(sqls):
#     i = 0
#     r = []
#     # 提交任务
#     for s in sqls:
#         current_app.logger.info(s)
#         str_key = list(s.keys())[0]
#         str_sql = list(s.values())[0]
#         current_app.logger.info('=================')
#         current_app.logger.info(str_key)
#         current_app.logger.info(str_sql)
#         current_app.logger.info('=================')
#         result = get_data_onesql.delay(str_sql)
#         r.append(result)
#     #等待多个任务完成
#
#     for result in r:
#         while not result.ready():
#             pass
#         current_app.logger.info('=================123')
#         current_app.logger.info(result.to_json())
#
#     return r





# def get_data_onesql_withmeta(datasource, sql):
#     db = None
#     df = None
#     try:
#         # db = get_db()
#         db = get_db(datasource)
#         print('exe sql=')
#         print(sql)
#
#         df = pd.read_sql(sql=sql, con=db)
#
#         print('hang==================================')
#         for indexs in df.columns:
#             print(indexs)
#             print(df.iloc[0][indexs])
#             print(type(df.iloc[0][indexs]))
#
#         for row in df.itertuples():
#             print(row)
#             # print(row[0],row[1])
#             # print(type(row[0]),   type(row[1]))
#
#     # cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
#         # cursor.execute(sql)
#         # #ret1 = cursor.fetchone()
#         # data = cursor.fetchall()
#         # print(data)
#         # for row in data:
#         #     print('hang==================================')
#         #     for col in row:
#         #         print( str(col) + '=' + str(row[col]) )
#         #
#         # for col in data[0]:
#         #     print(type(data[0][col]))
#
#
#         # df = pd.read_sql(sql=sql, con=db)
#         # time.sleep(sec)
#         # r = 'ok'
#         # print('types=====')
#         # print(df.types)
#         #
#         # print('result=====')
#         # print(df.to_json())
#     except Exception as e:
#         print('error:' )
#         print(e)
#     finally:
#         if db:
#             close_db()
#
#     # return r + '=======' + sql
#
#     # return df.to_json()
#     # 先返回dataframe对象
#     return 'ok'