import os

DIALECT = 'mysql'
DRIVER = 'pymysql'
USERNAME = os.getenv("WORK_USERNAME")
PASSWORD = os.getenv("WORK_PASSWORD")
HOST = os.getenv("HOST")
PORT = 3306
DATABASE = os.getenv("DBNAME")

class Config:
    SECRET_KEY = os.getenv("SECRET_WORK_KEY")
    SESSION_TYPE = 'filesystem'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    ACCESS_KEY = os.environ.get('ACCESS_KEY')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    URL = os.environ.get('URL')

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
