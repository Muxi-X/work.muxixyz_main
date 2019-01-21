from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from config import config

mail=Mail()
db=SQLAlchemy()
def create_app(config_name):
    app=Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    with app.app_context():
        db.init_app(app)

    mail.init_app(app)
    db.init_app(app)
    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint,url_prefix="/api/v1.0")
    return app


