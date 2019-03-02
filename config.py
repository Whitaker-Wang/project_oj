import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASKY_MAIL_SUBJECT_PREFIX = '[FLASKY]'
    FLASKY_MAIL_SENDER = '1059291245@qq.com'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    # QUESTIONS_PER_PAGE = int(os.environ.get('FLASKY_POSTS_PER_PAGE'))
    QUESTIONS_PER_PAGE = 10
    JSON_AS_ASCII = False
    QUEUE_SIZE = 4

    @staticmethod
    def init_app(app):
        pass


class DevelopementConfig(Config):
    DEBUG = True
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                              'sqlite:////' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
                             'sqlite:////' + os.path.join(basedir, 'data-dev.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                             'sqlite:////' + os.path.join(basedir, 'data-dev.sqlite')


config = {
    'development': DevelopementConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopementConfig
}
