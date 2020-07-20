#-*- coding: utf-8 -*-
from flask import Flask
from flask import make_response, jsonify, current_app, g
from celery import Celery
import logging
from logging import handlers

from myolap.handler import syshandler,homehandler,datahandler,olaphandler,modelconfighandler, olappermissionhandler
from myolap.config import  usingconfig
from concurrent.futures import ThreadPoolExecutor,as_completed
from flask_sqlalchemy import SQLAlchemy

from flask_apscheduler import APScheduler
from myolap.utils.nacosutils import send_hearbeat
import time

import nacos
import atexit
import fcntl

executor = ThreadPoolExecutor(usingconfig.MYOLAP_THREAD_POOL_SIZE)
sysdb = SQLAlchemy()
scheduler = APScheduler()




class Myolap(Flask):
    # executor = ThreadPoolExecutor(max_workers=5)
    datasource_pool ={}
    def __init__(self, *args, **kwargs):
        super(Myolap, self).__init__(__name__, *args, **kwargs)
        # Configure Myolap using our settings
        self.config.from_object(usingconfig)





def create_app():
    app = Myolap()
    init_logging(app, filename='/home/logs/myolap-server/myolap.log')
    app.register_blueprint(syshandler.handler, url_prefix=usingconfig.MYOLAP_URL_PREFIX)
    app.register_blueprint(homehandler.handler, url_prefix=usingconfig.MYOLAP_URL_PREFIX)
    app.register_blueprint(datahandler.handler, url_prefix=usingconfig.MYOLAP_URL_PREFIX)

    app.register_blueprint(olaphandler.handler, url_prefix=usingconfig.MYOLAP_URL_PREFIX)
    app.register_blueprint(modelconfighandler.handler, url_prefix=usingconfig.MYOLAP_URL_PREFIX)

    app.register_blueprint(olappermissionhandler.handler, url_prefix=usingconfig.MYOLAP_URL_PREFIX)


    celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'], backend=app.config['CELERY_RESULT_BACKEND'])
    celery.conf.update(app.config)

    sysdb.init_app(app)

    # 开发环境不注册
    # init_scheduler(app,scheduler)



    return app


def init_scheduler(app,scheduler):
    f = open("scheduler.lock", "wb")
    try:
        #linux fcntl
        # fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        # 初始化微服务nacos注册
        from myolap.utils.nacosutils import reg_nacos_client
        client = nacos.NacosClient(usingconfig.NACOS_SERVER_ADDRESSES, namespace=usingconfig.NACOS_NAMESPACE)
        client.default_timeout = 30

        reg_nacos_client(client)
        # 定时发送心跳任务
        scheduler.add_job(func=send_hearbeat, id='1', args=[client], trigger='interval',
                          seconds=usingconfig.NACOS_HEARTBEAT_INTERVAL, replace_existing=True)
        scheduler.start()

    except Exception as e:
        print('error: %s' %(e))
        pass

    def unlock():
        # fcntl.flock(f, fcntl.LOCK_UN)
        f.close()
    atexit.register(unlock)

def init_logging(app, filename,when='D',backCount=60,fmt='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'):
    format_str = logging.Formatter(fmt)  # 设置日志格式
    sh = logging.StreamHandler()  # 往屏幕上输出
    sh.setFormatter(format_str)  # 设置屏幕上显示的格式
    th = handlers.TimedRotatingFileHandler(filename=filename, when=when, backupCount=backCount,
                                           encoding='utf-8')  # 往文件里写入#指定间隔时间自动生成文件的处理器
    # 实例化TimedRotatingFileHandler
    # interval是时间间隔，backupCount是备份文件的个数，如果超过这个个数，就会自动删除，when是间隔的时间单位，单位有以下几种：
    # S 秒
    # M 分
    # H 小时、
    # D 天、
    # W 每星期（interval==0时代表星期一）
    # midnight 每天凌晨
    th.setFormatter(format_str)  # 设置文件里写入的格式
    app.logger.addHandler(sh)
    app.logger.addHandler(th)

    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'crit': logging.CRITICAL
    }

    logging.DEBUG
    app.logger.setLevel( level_relations.get(usingconfig.MYOLAP_LOG_LEVEL))  # 设置日志级别

# setup_logging(filename='/home/logs/myolap-server/myolap.log')


app = create_app()



@app.before_request
def init_session():
    g.session = sysdb.session()


@app.teardown_request
def close_session(self):
    g.session.close()



if __name__ == "__main__":
    print(app.url_map)
    app.run(port=usingconfig.MYOLAP_PORT,host=usingconfig.MYOLAP_IP)

    # service_name = 'testok'
    # cluster_name = ''
    #
    # client = nacos.NacosClient(usingconfig.NACOS_SERVER_ADDRESSES, namespace=usingconfig.NACOS_NAMESPACE)
    # client.default_timeout= 30
    # s= client.add_naming_instance(service_name, '10.12.12.69', 5000, cluster_name, 1, '{}', True, True)
    #
    # print(s)
    # print('==================')
    #
    # while (True):
    #     s = client.send_heartbeat(service_name, "10.12.12.69", 5000, cluster_name, 0.1, "{}")
    #     # s = client.send_heartbeat("myolap.bgpython", "10.12.12.69", 5000, "testCluster2", 0.1, "{}")
    #     print(s)
    #     print('=============================')
    #     time.sleep(5)
