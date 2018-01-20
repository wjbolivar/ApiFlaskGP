FROM python:2.7

MAINTAINER William Bolivar

ADD . /api

WORKDIR /api

RUN pip install -r requirements.txt

