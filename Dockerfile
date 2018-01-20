FROM ubuntu:16.04

MAINTAINER William Bolivar

ADD . /api

WORKDIR /api

RUN apt-get update
RUN apt-get install python python-pip -y
RUN apt-get install -y mongodb-org
RUN pip install -r requirements.txt

CMD python ./run.py
