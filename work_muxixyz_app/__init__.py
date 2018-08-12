from flask import Flask
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_pagedown import PageDown
from config import config

mail=Mail()
moment=Moment()
db=SQLAlchemy()
pagedown=PageDown()

login_manager=LoginManager()
login_manager.login_view='auth.login'

def create_app(config_name):
    app=Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    with app.app_context():
        db.init_app(app)

    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint,url_prefix="/api/v1.0/")
    return app


