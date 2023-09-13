FROM python:3.8.5-slim-buster

# set work directory
WORKDIR /usr/src/app

# set environment variables
# 임시 파일 업로드 방지
ENV PYTHONDONTWRITEBYTECODE 1
# 버퍼링 없이 바로 출력되게
ENV PYTHONUNBUFFERED 1

COPY . /usr/src/app/

# install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt