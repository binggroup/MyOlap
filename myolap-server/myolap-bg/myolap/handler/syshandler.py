# -*- coding: utf-8 -*-
# 说明： 后期实现菜单管理等功能在次添加

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify,current_app
)
import json



handler = Blueprint('sys', __name__)


@handler.route("/sys/login", methods=['POST'])
def login():

    data = json.loads(request.get_data())
    from myolap.model.sysdbmodel import SysUser
    u = SysUser.query.filter_by(username=data['username']).first()

    current_app.logger.info('sys login.........' + u.username + '=' + u.realname)
    r = jsonify({'a': 1, 'b': 2,'msg':'login ok'})

    return r