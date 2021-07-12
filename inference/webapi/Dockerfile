FROM python:3.6.9-slim-buster

RUN pip install -U pip && \
    pip install Flask==2.0.1

WORKDIR /workspace/tz
COPY . .

RUN pip install -e ./rmq_manager

ENV FLASK_APP=api
ENV FLASK_ENV=development
