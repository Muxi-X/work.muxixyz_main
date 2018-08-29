from flask import Flask,json
from flask_mail import Mail,Message
#from celery import Celery
#from celery_app import c
import time

app.config['MAIL_SERVER'] = 'smtp.qq.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEBUG'] = True
app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME'] = '1123948420@qq.com'
app.config['MAIL_PASSWORD'] = "hjl20030119"

mails=Mail(app)

def test():
    send_mail()

def send_mail():
    with app.app_context():
        subject="shiina's mail test!"
        body="hello,KOF"
        recipients=["897017426@qq.com"]
        mails.send(maketh_msg(subject,body,recipients))

def maketh_msg(subject,body,r):
    msg=Message(
        subject=subject,
        body=body,
        recipients=r
    )
    return msg

if __name__  == '__main__':
    app.run()
