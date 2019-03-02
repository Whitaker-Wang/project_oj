from functools import wraps
from flask import abort, g, jsonify, request

from app.api_1_0.authentication import Auth
from app.api_1_0.public import fail_return
from app.models import Permission, User


def identify(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        result = eval(Auth.identify(request).get_data().decode("utf-8"))
        if result['status'] and result['data']:
            user = User.get(result['data'])
            if not user.confirmed:
                return fail_return(msg='账号未激活')
            g.current_user = user
            return f(*args, **kwargs)
        else:
            return jsonify(result)
    return decorated_function


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.current_user.can(permission):
                return fail_return(msg='用户没有此权限')
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)
