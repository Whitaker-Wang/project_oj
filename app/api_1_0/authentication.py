import datetime, time

import jwt
from flask import g, jsonify, config, current_app

from app.api_1_0 import api, public
from app.api_1_0.public import DatabaseOperation
from app.models import User


class Auth(object):
    @staticmethod
    def encode_auth_token(user_id, login_time):
        """
        生成认证Token
        :param user_id: int
        :param login_time: int(timestamp)
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=10),
                'iat': datetime.datetime.utcnow(),
                'iss': 'ken',
                'data': {
                    'id': user_id,
                    'login_time': login_time
                }
            }
            return jwt.encode(
                payload,
                current_app.config['SECRET_KEY'],
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        验证Token
        :param auth_token:
        :return: integer|string
        """
        try:
            # payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'), leeway=datetime.timedelta(seconds=10))
            # 取消过期时间验证
            payload = jwt.decode(auth_token, current_app.config['SECRET_KEY'], options={'verify_exp': False})
            if 'data' in payload and 'id' in payload['data']:
                return payload
            else:
                raise jwt.InvalidTokenError
        except jwt.ExpiredSignatureError:
            return 'Token过期'
        except jwt.InvalidTokenError:
            return '无效Token'

    @staticmethod
    def authenticate(username, password):
        """
        用户登录，登录成功返回token，写将登录时间写入数据库；登录失败返回失败原因
        :param password:
        :return: json
        """
        user = User.query.filter_by(username=username).first()
        if user is None:
            return public.fail_return(data='', msg='找不到用户')
        else:
            if user.verity_password(password=password):
                if user.confirmed:
                    login_time = int(time.time())
                    user.login_time = login_time
                    DatabaseOperation.update()
                    token = Auth.encode_auth_token(user.id, login_time)
                    return public.success_return({"token": token.decode()}, '登录成功')
                else:
                    return public.fail_return(msg='账号未激活')
            else:
                return public.fail_return('', '密码不正确')

    @staticmethod
    def identify(request):
        """
        用户鉴权
        :return: json
        """
        auth_header = request.headers.get('Authorization')
        if auth_header:
            auth_token_arr = auth_header.split(" ")
            if not auth_token_arr or auth_token_arr[0] != 'JWT' or len(auth_token_arr) != 2:
                result = public.fail_return('', '请传递正确的验证头信息')
            else:
                auth_token = auth_token_arr[1]
                payload = Auth.decode_auth_token(auth_token)
                if not isinstance(payload, str):
                    user = User.query.filter_by(id=payload['data']['id']).first()
                    if user is None:
                        result = public.fail_return('', '找不到该用户信息')
                    else:
                        if user.login_time == payload['data']['login_time']:
                            result = public.success_return(user.id, '请求成功')
                        else:
                            result = public.fail_return('', 'Token已更改，请重新登录获取')
                else:
                    result = public.fail_return('', payload)
        else:
            result = public.fail_return('', '没有提供认证token')
        return result

