'''config for shinna'''
# import os
# basedir=os.path.abspath(os.path.dirname(__file__))

# class Config:
#     SECRET_KEY='CCNU MUXI BEST TEAM'
#     SQLALCHEMY_TRACK_MODIFICATIONS=False
#     FLASKY_MAIL_SUBJECT_PREFIX='[Flasky]'
#     FLASKY_MAIL_SENDER='Flasky Admin <shiina_orez@qq.com>'
#     FLASKY_ADMIN=os.environ.get('FLASKY_ADMIN')

#     @staticmethod
#     def init_app(app):
#         pass

# class DevelopmentConfig(Config):
#     DEBUG=True
#     MAIL_SERVER='smtp.qq.com'
#     MAIL_POST=465
#     MAIL_USE_TLS=True
#     MAIL_USERNAME=os.environ.get('MAIL_USERNAME')
#     MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD')
#     SQLALCHEMY_DATABASE_URI=\
#         'sqlite:///'+ os.path.join(basedir,'data-dev.sqlite')

# class TestingConfig(Config):
#     TESTING=True
#     SQLALCHEMY_DATABASE_URI=\
#         'sqlite:///'+ os.path.join(basedir, 'data-test.sqlite')

# class ProductionConfig(Config):
#     SQLALCHEMY_DATABASE_URI=\
#         'sqlite:///'+ os.path.join(basedir, 'data.sqlite')

# config={
#     'developments': DevelopmentConfig,
#     'testing': TestingConfig,
#     'production': ProductionConfig,
#     'default': DevelopmentConfig
# }

'''config for darren'''
import os

DIALECT = 'mysql'
DRIVER = 'pymysql'
USERNAME = 'root'  # os.environ.get('MYSQLUSER')
PASSWORD = 'root'  # os.environ.get('MYSQLPASSWORD')
HOST = '127.0.0.1'  # os.environ.get('MYSQLHOST')
PORT = '3306'
DATABASE = 'project'


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard ot guess string'
    SESSION_TYPE = 'filesystem'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = \
        "{}+{}://{}:{}@{}:{}/{}?charset=utf8".format(DIALECT,
                                                     DRIVER, USERNAME, PASSWORD, HOST, PORT,
                                                     DATABASE)


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = \
        "{}+{}://{}:{}@{}:{}/{}?charset=utf8".format(DIALECT,
                                                     DRIVER, USERNAME, PASSWORD, HOST, PORT,
                                                     DATABASE)


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = \
        "{}+{}://{}:{}@{}:{}/{}?charset=utf8".format(DIALECT,
                                                     DRIVER, USERNAME, PASSWORD, HOST, PORT,
                                                     DATABASE)

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)


config = {
    'developments': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
