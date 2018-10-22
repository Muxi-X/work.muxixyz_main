from flask import Flask, json, current_app
from flask_mail import Mail, Message
#from . import app
import time

app=Flask(__name__)

app.config['MAIL_SERVER'] = 'smtp.qq.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEBUG'] = True
app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME'] = ''
app.config['MAIL_PASSWORD'] = "uufmamibkidigbdh"

mails = Mail(app)

def send_mail(subject, body, recipients):
    with app.app_context():
        subject = "shiina's mail test!"
        body = "hello, I am the muxi-workbench."
        recipients = ["shiinaorez@gmail.com"]
        mails.send(maketh_msg(subject,
                              body,
                              recipients))

def maketh_msg(subject, body, r):
    msg = Message(subject = subject,
                  body = body,
                  recipients = r)
    return msg
