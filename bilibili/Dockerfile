FROM ubuntu:latest

MAINTAINER xiaolong "z13693763686@163.com"

RUN apt-get update -y && \  
    apt-get install -y python3-pip python3-dev

COPY . /

WORKDIR / 

RUN pip3 install -r requirements.txt




