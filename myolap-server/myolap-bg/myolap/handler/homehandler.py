# -*- coding: utf-8 -*-
# 说明： 后期实现

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify,current_app
)

handler = Blueprint('home', __name__)


@handler.route("/")
def index():
    current_app.logger.info('home page.........')
    from myolap.dataquery.dbtasks import printlog
    printlog()
    print('home page.......begin')
    print(current_app.config.get('MYSQL_HOST'))
    print('home page.......end')
    r='<h1>Welcome to MyOlap!</h1>'

    return r
