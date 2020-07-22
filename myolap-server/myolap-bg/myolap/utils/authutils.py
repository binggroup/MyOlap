# -*- coding: utf-8 -*-
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify,current_app
)
import json
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer
from itsdangerous import BadData
import base64

# secret_key = '1234567890adbcde'
# expires_in = 300  # 有效期单位为秒

from myolap.config import BaseConfig

# def generate_token():
#     """
#     # 生成token
#     """
#     # serializer = TJWSSerializer(秘钥, 有效期单位为秒)
#     serializer = TJWSSerializer(secret_key, expires_in,algorithm_name='HS256')
#
#     # serializer.dumps(数据), 返回bytes类型，比如对用户的id和email进行加密返回前端
#     data = {
#         'id': "hurenbing",
#         'email': "hooh_group@qq.com"
#     }
#     token = serializer.dumps(data)  # data为要加密的数据
#     token = token.decode()  # 得到返回后的带有效期和用户信息的加密token
#
#     return token

def get_current_username():
    token = request.headers.get('X-Access-Token')
    print('============')
    print(token)
    p2= token.split('.')[1]
    token_json = json.loads(base64.standard_b64decode(p2 + '==='))
    username = token_json['username']
    return username




# def check_token(token):
# 	# 验证失败，会抛出itsdangerous.BadData异常
# 	serializer = TJWSSerializer('cb362cfeefbf3d8d', expires_in,algorithm_name='HS256' )
#
# 	try:
# 		# 获取解密后的数据 bytes:dict
# 	    data = serializer.loads(token)
# 	except BadData:
# 	    return None
# 	else:
# 		# user_id = data.get('id')
# 		# user_email = data.get('email')
# 		return data


# a = generate_token()
# print(a)


#b='eyJhbGciOiJIUzUxMiIsImlhdCI6MTU5Mjg5OTk1NiwiZXhwIjoxNTkyOTAwMjU2fQ.eyJpZCI6Imh1cmVuYmluZyIsImVtYWlsIjoiaG9vaF9ncm91cEBxcS5jb20ifQ.CGlnqOKWRpC7Y7hnMjocqa5HL0riqfNKihVkyGul0UYwrtZ2_lNa-Q5eF9GQCQlBmYJJ6CXykvaMevdQSssadg'
# token='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1OTI5MDI0MzEsInVzZXJuYW1lIjoiYWRtaW4ifQ.qGtO2bLrcLoY7Gm7z6yd-Urpf0QzjCqj_vi4tOmj9go'
# bb = check_token(token)
# print(bb)
# print('=======')





from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_claims
)

from flask_jwt_extended import  decode_token

# from myolap.app import create_app
# app = create_app()
# app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
# jwt = JWTManager(app)

# 将上面生成的 jwt 进行解析认证
# import base64


# jwt_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsImtpZCI6Ijk1MjcifQ.eyJpYXQiOjE1NTkyNzY5NDEuNDIwODgzNywibmFtZSI6Imxvd21hbiJ9.GyQhOJK8FKD_Gd-ggSEDPPP1Avmz3M5NDVnmfOfrEIY"

#base64.decode('eyJpYXQiOjE1NTkyNzY5NDEuNDIwODgzNywibmFtZSI6Imxvd21hbiJ9')
# eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9
# eyJleHAiOjE1OTI5MDI0MzEsInVzZXJuYW1lIjoiYWRtaW4ifQ
# qGtO2bLrcLoY7Gm7z6yd-Urpf0QzjCqj_vi4tOmj9go
# s=base64.b64decode('eyJleHAiOjE1OTI5MDI0MzEsInVzZXJuYW1lIjoiYWRtaW4ifQ')
# str ='eyJleHAiOjE1OTI5MDI0MzEsInVzZXJuYW1lIjoiYWRtaW4ifQ==============='
# str='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9======'
# print(len(str))
# s=base64.b64decode(str, altchars="=", validate=True)
# print(s)

# ss= base64.standard_b64decode(str)
# print('jiema==')
# print(ss)
#
# a=b'{"exp":1592902431,"username":"admin"}'
# b=base64.b64encode(a)
# print(b)
# print(len(b))



# data = api_jwt.decode(jwt_token, "zhananbudanchou1234678", algorithms=['HS256'])
# jwt.decode_key_loader()
# with app.app_context():
#     token = create_access_token('admin', user_claims={"userid":"hurenbing"})
#     print('======token is ===========')
#     print(token)
#
#
#     data = decode_token(token,allow_expired=True)
#     # 解析出来的就是 payload 内的数据
#     print('======token jiemi ===========')
#     print(data)

import re
# string = 'abe(ac)ad)'
# string = ' 3 * (dcnt) + (dcnt3)'
# p1 = re.compile(r'[(](.*?)[)]', re.S) #最小匹配
# p2 = re.compile(r'[(](.*)[)]', re.S)  #贪婪匹配
# print(re.findall(p1, string))
# print(re.findall(p2, string))


string = ' 3 * [dcnt] + [dcnt3] + [abc]'
p1 = re.compile(r'[\[](.*?)[\]]', re.S) #最小匹配

print(re.findall(p1, string))

