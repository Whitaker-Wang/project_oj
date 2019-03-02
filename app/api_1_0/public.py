from flask import jsonify, url_for

from app import db
from app.Email import send_mail


def success_return(data=None, msg=None):
    """
    响应成功
    :param data:json/dict
    :param msg: str
    :return: json
    """
    return jsonify({
        "status": "Success",
        "data": data,
        "msg": msg
    })


def fail_return(data=None, msg=None):
    """
    响应失败
    :param data:json/dict
    :param msg: str
    :return: json
    """
    return jsonify({
        "status": "fail",
        "data": data,
        "msg": msg
    })


def send_token_email(user, func, token):
    send_mail(
        user.email, 'Confirm Your Account', 'email/'+func, user=user, token=token
    )
    return_user = user.to_json()
    return_user.update({'confirm': url_for('api.confirm', token=token, _external=True)})
    return success_return(
        data=return_user,
        msg="注册邮件发送成功，请点击链接确认")


class DatabaseOperation(object):
    """
    数据库增删改
    """
    @staticmethod
    def add(instance):
        db.session.add(instance)
        return DatabaseOperation.session_commit()

    @staticmethod
    def update():
        return DatabaseOperation.session_commit()

    @staticmethod
    def delete(instance, id=None):
        if id:
            instance.query.filter_by(id=id).delete()
        else:
            db.session.delete(instance)
        return DatabaseOperation.session_commit()

    @staticmethod
    def session_commit():
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            reason = str(e)
            return reason


def paging(pagination=None, page=1):
    """
    对资源内容进行分页
    :param pagination:Pagination
    :param page: int
    :return: json
    """
    if not pagination:
        return fail_return(msg='请输入正确的pagination')
    ins = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_questions', page=page - 1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_questions', page=page + 1, _external=True)
    return success_return(data={
        'ins': [que.to_json() for que in ins],
        'prev': prev,
        'next': next,
        'count': len(ins)
    }, msg='获取成功')