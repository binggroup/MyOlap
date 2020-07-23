#-*- coding: utf-8 -*-

from flask_sqlalchemy import SQLAlchemy
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify,current_app
)
# from sqlalchemy import Column, String, Integer, DateTime
from myolap.app import sysdb
from datetime import datetime
from sqlalchemy.databases import mysql

def single_to_dict(model):
    from sqlalchemy.orm import class_mapper

    columns = [c.key for c in class_mapper(model.__class__).columns]
    return dict((c, getattr(model, c)) for c in columns)

def single_to_dict_by_columns(model,columns):
    from sqlalchemy.orm import class_mapper
    # columns = [c.key for c in class_mapper(model.__class__).columns]
    return dict((c, getattr(model, c)) for c in columns)

def single_to_dict_by_columns2(model,columns,childkey):
    from sqlalchemy.orm import class_mapper
    # columns = [c.key for c in class_mapper(model.__class__).columns]
    dict ={}
    for col in columns:
        dict[col] = getattr(model,col)
    childobj = getattr(model,childkey)
    dict[childkey] =  multi_to_list(childobj)
    return dict
    # return dict((c, getattr(model, c)) for c in columns)

def multi_to_list(list):
    r = []
    for model in list:
        r.append(single_to_dict(model))
    return r

def multi_to_list_by_columns(list,columns):
    r = []
    for model in list:
        r.append(single_to_dict_by_columns(model,columns))
    return r

def multi_to_list_by_columns2(list,columns,childkey):
    #连子表对象也一并转json
    r = []
    for model in list:
        r.append(single_to_dict_by_columns2(model,columns,childkey))
    return r

class SysDataSource(sysdb.Model):
    # 定义表名
    __tablename__ = 'sys_data_source'
    # 定义列对象
    id = sysdb.Column(sysdb.Integer, primary_key=True)
    code = sysdb.Column(sysdb.String(100))
    name = sysdb.Column(sysdb.String(100))

    remark = sysdb.Column(sysdb.String(200))
    db_type = sysdb.Column(sysdb.String(10))
    db_driver = sysdb.Column(sysdb.String(100))
    db_url = sysdb.Column(sysdb.String(100))
    db_host = sysdb.Column(sysdb.String(100))
    db_port = sysdb.Column(sysdb.Integer)
    db_database= sysdb.Column(sysdb.String(100))

    db_name = sysdb.Column(sysdb.String(100))
    db_username = sysdb.Column(sysdb.String(100))
    db_password = sysdb.Column(sysdb.String(100))

    create_by = sysdb.Column(sysdb.String(50))
    create_time= sysdb.Column(sysdb.DateTime,  default=datetime.now)
    update_by = sysdb.Column(sysdb.String(50))
    update_time= sysdb.Column(sysdb.DateTime,  default=datetime.now, onupdate=datetime.now)
    sys_org_code= sysdb.Column(sysdb.String(64))

    remark


    # repr()方法显示一个可读字符串，虽然不是完全必要，不过用于调试和测试还是很不错的。
    def __repr__(self):
        return '<test {}>====={}===id is {} '.format(self.username,self.userid,self.autoid)




class SysUser(sysdb.Model):
    # 定义表名
    __tablename__ = 'sys_user'
    # 定义列对象
    id = sysdb.Column(sysdb.String(32), primary_key=True)
    #登录账号
    username = sysdb.Column(sysdb.String(100))
    realname = sysdb.Column(sysdb.String(100))

    password = sysdb.Column(sysdb.String(255))
    salt = sysdb.Column(sysdb.String(45))
    email = sysdb.Column(sysdb.String(45))


    create_by = sysdb.Column(sysdb.String(50))
    create_time= sysdb.Column(sysdb.DateTime,  default=datetime.now)
    update_by = sysdb.Column(sysdb.String(50))
    update_time= sysdb.Column(sysdb.DateTime,  default=datetime.now, onupdate=datetime.now)


    # repr()方法显示一个可读字符串，虽然不是完全必要，不过用于调试和测试还是很不错的。
    def __repr__(self):
        return '<test {}>====={}===id is {} '.format(self.username,self.realname,self.autoid)


class OlapModelConfig(sysdb.Model):
    # 定义表名
    __tablename__ = 'olap_model_config'
    # 定义列对象
    id = sysdb.Column(sysdb.Integer, primary_key=True)
    # 登录账号
    model_name = sysdb.Column(sysdb.String(50),unique=True)
    datasource_name = sysdb.Column(sysdb.String(50))

    db_type = sysdb.Column(sysdb.String(20))
    model_sql = sysdb.Column(sysdb.String(50000))

    meta_data = sysdb.relationship('OlapModelConfigMetadata',backref='olap_model_config')

    def __repr__(self):
        return 'the model：{} is {}'.format(self.model_name,self.datasource_name)


class OlapModelConfigMetadata(sysdb.Model):
    # 定义表名
    __tablename__ = 'olap_model_config_metadata'
    # 定义列对象
    id = sysdb.Column(sysdb.Integer, primary_key=True)
    # 父id
    pid = sysdb.Column(sysdb.Integer, sysdb.ForeignKey('olap_model_config.id'))

    sql_field = sysdb.Column(sysdb.String(500))

    sql_field_type = sysdb.Column(sysdb.String(50))
    # column_alias = sysdb.Column(String(50))
    # column_type = sysdb.Column(Integer)
    def __repr__(self):
        return 'the meta_data ：{} is {}'.format(self.pid, self.sql_field)


class OlapDimension(sysdb.Model):
    # 定义表名
    __tablename__ = 'olap_dimension'
    # 定义列对象
    olap_id = sysdb.Column(sysdb.String(32), primary_key=True)

    dimension_name = sysdb.Column(sysdb.String(100))
    checked_list = sysdb.Column(mysql.MSMediumText)
    filter_list = sysdb.Column(mysql.MSMediumText)

    permission = sysdb.relationship('OlapDimensionPermission', backref='olap_dimension')

    create_by = sysdb.Column(sysdb.String(50))
    create_time= sysdb.Column(sysdb.DateTime, default=datetime.now)

    version = sysdb.Column(sysdb.String(10))

    def __repr__(self):
        return 'the meta_data ：{} is {}'.format(self.dimension_name, self.olap_id)



class OlapDimensionShortcut(sysdb.Model):
    # 定义表名
    __tablename__ = 'olap_dimension_shortcut'
    # 定义列对象
    id = sysdb.Column(sysdb.String(32), primary_key=True)
    olap_id = sysdb.Column(sysdb.String(32))
    shortcut_name = sysdb.Column(sysdb.String(100))
    checked_list = sysdb.Column(mysql.MSMediumText)
    filter_list = sysdb.Column(mysql.MSMediumText)
    create_by = sysdb.Column(sysdb.String(50))
    create_time= sysdb.Column(sysdb.DateTime, default=datetime.now)
    version = sysdb.Column(sysdb.String(10))

    def __repr__(self):
        return 'the meta_data ：{} is {}'.format(self.shortcut_name, self.id)


class OlapDimensionPermission(sysdb.Model):
    # 定义表名
    __tablename__ = 'olap_dimension_permission'
    # 定义列对象
    id = sysdb.Column(sysdb.Integer, primary_key=True)
    olap_id = sysdb.Column(sysdb.String(32), sysdb.ForeignKey('olap_dimension.olap_id'))

    username = sysdb.Column(sysdb.String(100))
    row_permission = sysdb.Column(sysdb.String(2000))
    col_permission = sysdb.Column(sysdb.String(5000))
    create_by = sysdb.Column(sysdb.String(50))
    create_time= sysdb.Column(sysdb.DateTime, default=datetime.now)
    version = sysdb.Column(sysdb.String(10))

    def __repr__(self):
        return 'the meta_data ：{} is {}'.format(self.username, self.id)
