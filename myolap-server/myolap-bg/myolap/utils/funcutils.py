# -*- coding: utf-8 -*-

import re


def get_sql_field(sql_express):
    # string = ' 3 * [dcnt] + [dcnt3] + [abc]'
    p = re.compile(r'[\[](.*?)[\]]', re.S)   #最小匹配  匹配所有[]包围的字符串
    list =  re.findall(p, sql_express)
    sql_field = {}
    for item in list:

        sql_field[item.strip()] = 1
    return sql_field



def get_pandas_express(sql_field,sql_express):
    #跟进用户填写的跨模型字段公式，得到pandas识别的公式
    #目前最简单的是，去掉中括号[] 得到真实字段
    result = sql_field + ' = ' +sql_express.replace('[' ,' ').replace(']',' ')
    return result