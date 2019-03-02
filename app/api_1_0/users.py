# -*- coding:utf8 -*-

from flask import request, jsonify, url_for, g

from app.api_1_0.authentication import Auth
from app.api_1_0.decorators import identify, permission_required
from app.api_1_0.public import success_return, fail_return, send_token_email, DatabaseOperation
from app.models import User, Permission
from . import api


@api.route('login/', methods=['POST'])
def login():
    """
    用户登录
    :return:json
    """
    username = request.form.get('username')
    password = request.form.get('password')
    if not username or not password:
        return fail_return(msg="用户名和密码不能为空")
    else:
        return Auth.authenticate(username=username, password=password)


@api.route('register/', methods=['POST', 'PUT'])
def register():
    """
    用户注册
    :return:json
    """
    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get("password")
    if not email or not username or not password:
        return fail_return("", "用户名、密码和邮件不能为空")
    if User.query.filter_by(email=email).first():
        return fail_return(msg="邮箱已被注册")
    if User.query.filter_by(username=username).first():
        return fail_return(msg="用户名已被注册")

    user = User(username=username, email=email, password=password)
    result = DatabaseOperation.add(user)
    if user.id:
        token = user.generate_confirmation_token()
        send_token_email(user, "confirm", token)
        return success_return(user.to_json(), "邮件发送成功")
    else:
        print(result)
        return fail_return(msg="用户注册失败")


@api.route('/user/<int:id>', methods=['GET'])
def get_user(id):
    """
    获取用户的信息
    :return:json
    """
    user = User.query.filter_by(id=id).first()
    if not user:
        return fail_return({"id": id}, '用户不存在')
    return success_return(user.to_json(), "获取成功")


@api.route('/confirm/<token>', methods=['GET'])
def confirm(token):
    """
    确认邮件激活用户
    :param token: str
    :return: json
    """
    id = User.confirm(token)
    user = User.query.filter_by(id=id).first()
    if not user:
        return fail_return(msg='用户不存在')
    if user.confirmed:
        return fail_return(msg='用户已激活')
    user.confirmed = True
    DatabaseOperation.update()
    return success_return(data=user.to_json(), msg='激活成功')


@api.route('/resend/', methods=['POST'])
def reconfirm():
    """
    重新发送邮件进行确认
    :return: json
    """
    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username=username).first()
    if user:
        if user.verity_password(password):
            token = user.generate_confirmation_token()
            send_token_email(user, "confirm", token)
            return success_return(user.to_json(), "邮件发送成功")
        else:
            return fail_return(msg="密码错误")
    else:
        return fail_return(msg="用户不存在")


@api.route('/changePwd/', methods=['POST'])
@identify
def change_pwd():
    """
    修改密码（登录状态下）
    :return:
    """
    old_pwd = request.form.get('oldPwd')
    if not old_pwd:
        return fail_return(msg="密码不能为空")
    if g.current_user.verity_password(old_pwd):
        new_pwd = request.form.get('newPwd')
        if not new_pwd:
            return fail_return(msg="密码不能为空")
        g.current_user.password = new_pwd
        DatabaseOperation.update()
        return success_return(g.current_user.to_json(), "密码修改成功")
    else:
        return fail_return(msg='原密码错误')


@api.route('/forgetPwd/', methods=['POST'])
def forget_pwd():
    """
    忘记密码发送邮件找回密码
    :return:
    """
    email = request.form.get('email')
    user = User.query.filter_by(email=email).first()
    token = user.generate_confirmation_token()

    if user:
        user.find_pwd_token = token
        DatabaseOperation.update()
        send_token_email(user, "changePwd", token)
        return success_return(data={'find_password_url': url_for('api.find_pwd', token=token, _external=True)}
                              , msg='邮件已发送')
    return fail_return(msg="用户不存在")


@api.route('/findPwd/<token>', methods=['GET', 'POST'])
def find_pwd(token):
    """
    点击邮件链接 找回密码
    :param token: str
    :return:
    """
    id = User.confirm(token)
    email = request.form.get('email')
    user = User.query.filter_by(id=id).first()
    user1 = User.query.filter_by(email=email).first()
    if user and user1 and user is user1:
        if user.find_pwd_token != token:
            return fail_return(msg="链接失效")
        new_password = request.form.get('newPwd')
        if not new_password:
            return fail_return(msg="密码不能为空")
        user.password = new_password
        user.find_pwd_token = None
        DatabaseOperation.update()
        return success_return(user.to_json(), "密码修改成功")
    return fail_return("用户不存在")


@api.route('/changeName/', methods=['POST'])
@identify
def change_name():
    """
    修改用户名名字
    :return:
    """
    new_name = request.form.get('newName')
    if not new_name:
        return fail_return(msg="名字不能为空")
    user = User.query.filter_by(username=new_name).first()
    if user:
        return fail_return(msg="用户名已存在")
    g.current_user.username = new_name
    DatabaseOperation.update()
    return success_return(g.current_user.to_json(), "用户名修改成功")


@api.route('/deleteUser/<id>', methods=['POST', 'GET', 'DELETE'])
@identify
@permission_required(Permission.MODIFY_USER)
def delete_user(id):
    """
    删除用户
    :param id:
    :return:
    """
    user = User.get(id)
    if not user:
        return fail_return(msg='用户不存在')
    DatabaseOperation.delete(user, id)
    return success_return(g.current_user.to_json(), msg='用户已删除')
