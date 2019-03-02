from flask import request, g, url_for, jsonify, current_app
from sqlalchemy import func

from app import db
from app.api_1_0 import api
from app.api_1_0.decorators import identify, permission_required
from app.api_1_0.public import success_return, fail_return, DatabaseOperation, paging
from app.models import Question, Permission, User, ComQue, Data2Test, Submit


@api.route('/question/<int:id>', methods=['GET', 'POST'])
def get_question(id=None):
    """
    获取id所对应的题目信息
    :param id: int
    :return: json
    """
    question = Question.get_question(id)
    if question:
        return success_return(question.to_json(), "获取成功")
    return fail_return(msg="所查id对应的题目不存在")


@api.route('/addQue/', methods=['POST', 'PUT'])
@identify
@permission_required(Permission.MODIFY_QUES)
def add_question():
    """
    添加题目
    :return: json
    """
    topic = request.form.get('topic')
    content = request.form.get('content')
    notes = request.form.get('notes')
    example = request.form.get('example')
    maker = g.current_user

    input_type = request.form.get('input_type')
    input_data = request.form.get('input_data')
    output_type = request.form.get('output_type')
    output_data = request.form.get('output_data')

    if topic and content:
        que = Question(topic=topic, content=content, notes=notes, example=example, maker=maker)
        DatabaseOperation.add(que)
        if que:
            if input_data and input_type and output_data and output_type:
                data = Data2Test(input_data=input_data, input_type=input_type,
                                 output_data=output_data, output_type=output_type, question=que)
                if data:
                    DatabaseOperation.add(data)
                    return success_return(que.to_json(), '添加成功')
                return fail_return(msg="题目添加成功，数据添加出错")
            return success_return(que.to_json(), '添加成功')
        return fail_return(msg='添加失败')
    return fail_return('题目和内容不能为空')


@api.route('/deleteQue/<id>', methods=['POST', 'GET', 'DELETE'])
@identify
@permission_required(Permission.MODIFY_QUES)
def delete_question(id):
    """
    删除题目
    :param id:
    :return:
    """
    q = Question.get_question(id)
    if not q:
        return fail_return(msg='所对应题目不存在')
    # data = Data2Test.query.filter_by(que_id=id)
    # print(data.que_id)
    # if data:
    #     DatabaseOperation.delete(data)
    DatabaseOperation.delete(q, id)
    return success_return(msg='删除成功')


@api.route('/modifyQue/<id>', methods=['POST'])
@identify
@permission_required(Permission.MODIFY_QUES)
def modify_question(id):
    """
    修改题目信息
    :param id:
    :return:
    """
    que = Question.query.filter_by(id=id).first()
    if not que:
        return fail_return(msg='所对应题目不存在')
    topic = request.form.get('topic')
    content = request.form.get('content')
    notes = request.form.get('notes')
    example = request.form.get('example')
    if topic and content:
        que.topic = topic
        que.content = content
        que.notes = notes
        que.example = example
        DatabaseOperation.update()
        return success_return(que.to_json(), '修改成功')
    return fail_return('题目和内容不能为空')


@api.route('/questions/', methods=['GET', 'POST'])
def get_questions():
    """
    获得题目 分页后的资源
    :return:
    """
    page = request.args.get('page', 1, type=int)
    pagination = Question.query.paginate(
        page, per_page=current_app.config['QUESTIONS_PER_PAGE'],
        error_out=False
    )
    return paging(pagination, page)


@api.route('/getData/<id>/', methods=['GET'])
@identify
@permission_required(Permission.MODIFY_QUES)
def get_data(id):
    """获取对应的题目的数据案例"""
    q = Question.get_question(id)
    if not q:
        return fail_return(msg="该题不存在")
    ds = q.data.all()
    json_ds = [json_data.to_json() for json_data in ds]
    return success_return(json_ds, msg="获取成功")


@api.route('/deleteData/<id>/<putD>', methods=['DELETE'])
@identify
@permission_required(Permission.MODIFY_QUES)
def delete_data(id, putD):
    """
    删除数据
    """
    q = Question.get_question(id)
    if not q:
        return fail_return("题目不存在")
    d = Data2Test.query.filter_by(que_id=id, input_data=putD).first()
    DatabaseOperation.delete(d)
    return success_return(msg="删除成功")


@api.route('/modifyData/<id>/<string:putD>', methods=['POST'])
@identify
@permission_required(Permission.MODIFY_QUES)
def modify_data(id, putD):
    """
    修改题目的输入和输出数据
    """
    q = Question.get_question(id)
    if not q:
        return fail_return("题目不存在")
    d = Data2Test.query.filter_by(que_id=id, input_data=putD).first()
    if d:
        d.input_type = request.form.get('input_type')
        d.input_data = request.form.get('input_data')
        d.output_type = request.form.get('output_type')
        d.output_data = request.form.get('output_data')
        d.time_limit = request.form.get('time_limit')
        d.mem_limit = request.form.get('mem_limit')
        return success_return(d.to_json(), "修改成功")
    return fail_return(msg="修改失败")


@api.route('/addData/<id>', methods=['PUT'])
@identify
@permission_required(Permission.MODIFY_QUES)
def add_data(id):
    """添加数据"""
    q = Question.get_question(id)
    input_type = request.form.get('input_type')
    input_data = request.form.get('input_data')
    output_type = request.form.get('output_type')
    output_data = request.form.get('output_data')
    time_limit = request.form.get('time_limit')
    mem_limit = request.form.get('mem_limit')
    d = Data2Test(input_data=input_data, input_type=input_type, output_data=output_data,
                  output_type=output_type, question=q, time_limit=time_limit, mem_limit=mem_limit)
    if d:
        DatabaseOperation.add(d)
        return success_return(d.to_json(), "添加成功")
    return fail_return(msg="添加失败")


@api.route('/ranking/', methods=['GET', 'POST'])
def ranking():
    """
    完成题数排行榜
    返回分页后排行榜资源
    :return:
    """
    page = request.args.get('page', 1, type=int)
    com_ques_sub = ComQue.query.group_by(ComQue.user_id).\
        with_entities(ComQue.user_id, func.count(ComQue.user_id).label('count')).subquery()
    # print(com_ques_sub.c.user_id)
    pagination = db.session.query(User).join(com_ques_sub, User.id == com_ques_sub.c.user_id).\
        order_by(com_ques_sub.c.count.desc()).paginate(
        page=page, per_page=current_app.config['QUESTIONS_PER_PAGE'],
        error_out=False
    )
    return paging(pagination, page)


@api.route('/comUsers/<int:id>', methods=['GET', 'POST'])
def get_complete_users(id):
    """
    获得完成该题目的用户 分页后的资源
    """
    page = request.args.get('page', 1, type=int)
    que = Question.get_question(id)
    if not que:
        return fail_return(msg='题目不存在')
    sub = ComQue.query.filter_by(question_id=id).with_entities(ComQue.user_id, ComQue.timestamp).subquery()
    # print(sub)
    pagination = db.session.query(User).join(sub, sub.c.user_id == User.id).order_by(sub.c.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['QUESTIONS_PER_PAGE'], error_out=False
    )
    return paging(pagination, page)


@api.route('/comQues/<int:id>', methods=['GET', 'POST'])
def get_complete_questions(id):
    """
    获得该用户完成的题目 分页后的资源
    """
    page = request.args.get('page')
    user = User.get(id)
    if not user:
        return fail_return(msg='用户不存在')
    sub = ComQue.query.filter_by(user_id=id).with_entities(ComQue.question_id, ComQue.timestamp).subquery()
    # print(sub)
    pagination = db.session.query(Question).join(sub, sub.c.question_id == Question.id)\
        .order_by(sub.c.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['QUESTIONS_PER_PAGE'], error_out=False
    )
    return paging(pagination, page)


@api.route('/submit/<int:id>', methods=['PUT', 'POST'])
@identify
@permission_required(Permission.SUBMIT)
def submit(id):
    """提交代码"""
    language = request.form.get('language')
    content = request.form.get('content')
    sub = Submit(language=language, content=content, user=g.current_user, question=Question.get_question(id))
    if sub:
        DatabaseOperation.add(sub)
        return success_return(sub.to_json(), "提交成功")
    return fail_return(msg="提交失败")


# @api.route('/test', methods=['GET'])
# def test():
#     d = Data2Test.query.filter_by(que_id=92).first()
#     print(d)
#     return success_return()
