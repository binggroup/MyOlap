# -*- coding: utf-8 -*-

import os
import logging
BASEDIR = os.path.abspath(os.path.dirname(__file__))

class BaseConfig:
    """base config"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'myolap secret key'
    MYOLAP_THREAD_POOL_SIZE = 10
    MYOLAP_URL_PREFIX= '/'
    MYOLAP_LOG_LEVEL= 'debug'

    MYOLAP_IP = '10.12.12.69'
    MYOLAP_PORT ='5000'


class TestConfig(BaseConfig):
    """MYSQL 数据库配置信息 注意关键字要大写"""
    MYSQL_HOST = '10.129.129.156'
    MYSQL_PORT = 3306
    MYSQL_USER = 'mbi'
    MYSQL_PWD = 'zxcvb'
    MYSQL_DATABASE = 'myolap'

    #app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://jianshu:jianshu@127.0.0.1:3306/jianshu'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + MYSQL_USER + ':' + MYSQL_PWD + '@' + MYSQL_HOST + ':' + str(MYSQL_PORT) + '/' + MYSQL_DATABASE
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_ECHO = True
    #=连接池大小
    SQLALCHEMY_POOL_SIZE = 3
    #mysql回收连接配置
    SQLALCHEMY_POOL_RECYCLE = 1200

    REDIS_HOST = ''
    CELERY_BROKER_URL = 'redis://10.129.129.156:6379/3'
    CELERY_RESULT_BACKEND = 'redis://10.129.129.156:6379/3'

    FLASKY_MAIL_SENDER = 'hurenbing@cyou-inc.com'  # 发件人地址
    FLASKY_MAIL_SUBJECT_PREFIX = '[MYOLAP]'  # 邮件主题前缀


    NACOS_SERVER_ADDRESSES='10.129.128.65:8855'
    NACOS_SERVICE_NAME='myolapbg'
    NACOS_NAMESPACE='b73e7cf6-44a7-4285-8d7b-ae4095049b98'
    NACOS_TIMEOUT = 30
    NACOS_HEARTBEAT_INTERVAL = 10

    MYOLAP_IP = '10.12.12.69'
    MYOLAP_PORT = '5000'

    LOG_LEVEL = logging.DEBUG


class ProductionConfig(BaseConfig):
    """运行环境配置"""
    MYSQL_HOST = '10.129.129.156'
    MYSQL_PORT = 3306
    MYSQL_USER = 'mbi'
    MYSQL_PWD = 'zxcvb'
    MYSQL_DATABASE = 'myolap_test'

    # app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://jianshu:jianshu@127.0.0.1:3306/jianshu'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + MYSQL_USER + ':' + MYSQL_PWD + '@' + MYSQL_HOST + ':' + str(
        MYSQL_PORT) + '/' + MYSQL_DATABASE
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_ECHO = True
    # =连接池大小
    SQLALCHEMY_POOL_SIZE = 3
    # mysql回收连接配置
    SQLALCHEMY_POOL_RECYCLE = 1200

    REDIS_HOST = ''
    CELERY_BROKER_URL = 'redis://10.129.129.156:6379/3'
    CELERY_RESULT_BACKEND = 'redis://10.129.129.156:6379/3'

    FLASKY_MAIL_SENDER = 'hurenbing@cyou-inc.com'  # 发件人地址
    FLASKY_MAIL_SUBJECT_PREFIX = '[MYOLAP]'  # 邮件主题前缀

    NACOS_SERVER_ADDRESSES = '10.129.128.65:8855'
    NACOS_SERVICE_NAME = 'myolapbg'
    NACOS_NAMESPACE = 'b73e7cf6-44a7-4285-8d7b-ae4095049b98'
    NACOS_TIMEOUT = 30
    NACOS_HEARTBEAT_INTERVAL = 10

    MYOLAP_IP = '10.129.129.156'
    MYOLAP_PORT = '5000'

    LOG_LEVEL = logging.DEBUG



# config = {
#     'test': TestConfig,
#     'production': ProductionConfig
# }

usingconfig = TestConfig
