FROM python:3.5
MAINTAINER kasheemlew <kasheemirvinglew@gmail.com>

ENV DEPLOY_PATH /workebench_be_main

RUN mkdir -p $DEPLOY_PATH
WORKDIR $DEPLOY_PATH

Add requirements.txt requirements.txt
RUN pip install --index-url http://pypi.doubanio.com/simple/ -r requirements.txt --trusted-host=pypi.doubanio.com

Add . .
