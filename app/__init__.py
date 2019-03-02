from flask import Flask, request, current_app
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import config
# from flask_login import LoginManager
import pymysql
from flask_pagedown import PageDown
# from flask_wtf import CSRFProtect
# from flask_jwt import JWT


pymysql.install_as_MySQLdb()

mail = Mail()
moment = Moment()
db = SQLAlchemy()
# login_manager = LoginManager()
# login_manager.session_protection = 'strong'
# login_manager.login_view = 'auth.login'
pagedown = PageDown()
# csrf = CSRFProtect()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    # print(current_app.config['SECRET_KEY'])

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        if request.method == 'OPTIONS':
            response.headers['Access-Control-Allow-Methods'] = 'DELETE, GET, POST, PUT'
            headers = request.headers.get('Access-Control-Request-Headers')
            if headers:
                response.headers['Access-Control-Allow-Headers'] = headers
        return response

    pagedown.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    # csrf.init_app(app)
    # login_manager.init_app(app)

    from .api_1_0 import api as api_1_0_blueprint
    app.register_blueprint(api_1_0_blueprint, url_prefix='/v1.0')

    return app
