FROM python:3.6.9-slim-buster

RUN pip install -U pip && \
    pip install Flask==2.0.1

WORKDIR /workspace/webapi
COPY webapi .
COPY rmq_manager /workspace/webapi/rmq_manager

RUN pip install -e ./rmq_manager

ENV FLASK_APP=api
ENV FLASK_ENV=development
