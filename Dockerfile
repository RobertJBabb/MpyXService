FROM ubuntu:16.04

MAINTAINER Robert Babb "rjb_github@dragonflythingworks.com"

RUN apt-get update -y
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN apt-get install -y python3-venv

RUN adduser --disabled-password --gecos "" mpyxservice

WORKDIR /home/mpyxservice

# We copy just the files first to leverage Docker cache
COPY . .

RUN python3 -m venv venv
RUN venv/bin/pip install --upgrade pip
RUN venv/bin/pip install gunicorn
RUN venv/bin/pip install mpy-cross
RUN venv/bin/pip install -r requirements.txt

RUN chmod +x boot.sh

ENV FLASK_APP main.py

RUN chown -R mpyxservice:mpyxservice ./
USER mpyxservice

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
