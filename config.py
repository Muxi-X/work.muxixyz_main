'''config for shinna'''
import os

DIALECT = 'mysql'
DRIVER = 'pymysql'
USERNAME = 'muxitest'
PASSWORD = 'Muxitest304'
HOST = 'rm-wz907gsr637s950hmjo.mysql.rds.aliyuncs.com'
PORT = '3306'
DATABASE = 'workbenchtest'

class Config:
    SECRET_KEY = 'work.muxixyz'
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
        "{}+{}://{}:{}@{}:{}/{}?charset=utf8".format(
            DIALECT,
            DRIVER, 
            USERNAME, 
            PASSWORD, 
            HOST, 
            PORT,
            DATABASE
        )

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = \
        "{}+{}://{}:{}@{}:{}/{}?charset=utf8".format(
            DIALECT,
            DRIVER, 
            USERNAME, 
            PASSWORD, 
            HOST, 
            PORT,
            DATABASE
        )


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = \
        "{}+{}://{}:{}@{}:{}/{}?charset=utf8".format(
            DIALECT,
            DRIVER, 
            USERNAME, 
            PASSWORD, 
            HOST, 
            PORT,
            DATABASE
        )

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)


config = {
    'developments': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}  

"""'''config for darren'''
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
"""
