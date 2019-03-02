from datetime import datetime
from random import randint

import bleach
from flask import current_app, url_for
# from flask_login import AnonymousUserMixin, UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from markdown import markdown
from pymysql import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

from . import db


class Permission(object):
    """
    用户权限
    SUBMIT: 提交题目
    """
    SUBMIT = 0X01
    MODIFY_QUES = 0X02
    MODIFY_USER = 0X04
    ADMINISTER = 0x80
    # COMMENT = 0x08
    # MODERATE_COMMENTS = 0x0f


class Role(db.Model):
    """
    用户角色：匿名用户、普通用户、管理员
    """
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')
    default = db.Column(db.Boolean, default=False, index=True)

    @staticmethod
    def insert_roles():
        roles = {
            'User': (
                Permission.SUBMIT, True
            ),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()


class ComQue(db.Model):
    """
    关联表
    用户完成的题目
    """
    __tablename__ = 'com_ques'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'),
                        primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id', ondelete='CASCADE', onupdate='CASCADE')
                            , primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow().replace(hour=datetime.utcnow().hour+8))


class User(db.Model):
    """
    用户信息
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64), unique=True, index=True)
    login_time = db.Column(db.Integer)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    find_pwd_token = db.Column(db.String(256))

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id',  ondelete='CASCADE', onupdate='CASCADE'), index=True)
    com_questions = db.relationship('ComQue', foreign_keys=[ComQue.user_id], backref=db.backref('user', lazy='joined'),
                                    lazy='dynamic', cascade='all, delete-orphan')
    issue_ques = db.relationship('Question', backref='maker', lazy='dynamic')
    submits = db.relationship('Submit', backref='user',
                              lazy='dynamic', cascade='all, delete-orphan')

    def __init__(self, username=None, email=None, login_time=None, password=None, **kwargs):
        self.username = username
        self.email = email
        self.login_time = login_time
        self.password = password
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        # if self.email is not None and self.avatar_hash is None:
        #     self.avatar_hash = hashlib.md5(
        #         self.email.encode('utf-8')).hexdigest()

    def __str__(self):
        return "User(id='%s')" % self.id

    def to_json(self):
        json_user = {
            'url': url_for('api.get_complete_questions', id=self.id, _external=True),
            'login_time': self.login_time,
            'username': self.username,
            # 'completed_questions': self.com_questions,
            'completed_questions_count': self.com_questions.count(),
            'is_administrator': self.can(Permission.ADMINISTER)
        }
        return json_user

    @staticmethod
    def get(uid):
        return User.query.filter_by(id=uid).first()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verity_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    @staticmethod
    def confirm(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except Exception as e:
            return str(e)
        return data.get('confirm')

    def can(self, permissions):
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    @staticmethod
    def generate_fake(count=100):
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.name.full_name(),
                     password=forgery_py.lorem_ipsum.word(),
                     login_time=None,
                     confirmed=True,
                     find_pwd_token=None)
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()


class Question(db.Model):
    """
    题库
    maker: 发布该题目的用户
    """
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(64))
    content = db.Column(db.Text)
    content_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow().replace(hour=datetime.utcnow().hour+8))
    example = db.Column(db.Text)
    notes = db.Column(db.Text)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'))
    com_users = db.relationship('ComQue', foreign_keys=[ComQue.question_id],
                                backref=db.backref('question', lazy='joined'),
                                lazy='dynamic', cascade='all, delete-orphan')
    data = db.relationship('Data2Test', backref='question',
                           lazy='dynamic', cascade='all, delete-orphan')
    submits = db.relationship('Submit', backref='question',
                              lazy='dynamic', cascade='all, delete-orphan')

    @staticmethod
    def get_question(id):
        return Question.query.filter_by(id=id).first()

    @staticmethod
    def on_changed_content(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote',
                        'code', 'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True
        ))

    def to_json(self):
        json_question = {
            'url': url_for('api.get_question', id=self.id, _external=True),
            'topic': self.topic,
            'content': self.content,
            'timestamp': self.timestamp,
            'question_maker': {'id': self.maker.id, 'username': self.maker.username},
            'completed_count': self.com_users.count()
        }
        return json_question

    @staticmethod
    def generate_fake(count=100):
        from random import seed
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            q = Question(topic=forgery_py.internet.user_name(),
                         content=forgery_py.lorem_ipsum.sentence(),
                         timestamp=forgery_py.date.date(True),
                         maker=u
                         )
            db.session.add(q)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


db.event.listen(Question.content, 'set', Question.on_changed_content)


class Submit(db.Model):
    """
    用户提交还未处理的问题
    """
    __tablename__ = 'submission'
    id = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.String(64))
    content = db.Column(db.Text, default=None)
    message = db.Column(db.Text, default="waiting")

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'))
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id', ondelete='CASCADE', onupdate='CASCADE'))

    def to_json(self):
        json_sub = {
            'language': self.language,
            'content': self.content,
            'user_id': self.user_id,
            'question_id': self.question_id,
            'message': self.message
        }
        return json_sub


class Data2Test(db.Model):
    """
    题目输入输出的案例
    """
    __tablename__ = 'data'
    input_type = db.Column(db.String(32), default=None)
    input_data = db.Column(db.Text, default=None)
    output_type = db.Column(db.String(32), default=None)
    output_data = db.Column(db.Text, default=None)
    time_limit = db.Column(db.Integer, default=2000)
    mem_limit = db.Column(db.Integer, default=65536)

    que_id = db.Column(db.Integer, db.ForeignKey('questions.id', ondelete='CASCADE', onupdate='CASCADE'),
                       primary_key=True)

    def to_json(self):
        json_data = {
            'url': url_for('api.get_data', id=self.que_id, _external=True),
            'input_type': self.input_type,
            'input_data': self.input_data,
            'output_type': self.output_type,
            'out_data': self.output_data,
            'time_limit': self.time_limit,
            'mem_limit': self.mem_limit
        }
        return json_data
