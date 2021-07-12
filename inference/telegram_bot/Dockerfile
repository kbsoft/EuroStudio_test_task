FROM python:3.6.9-slim-buster

RUN pip install -U pip && \
    pip install python-telegram-bot==13.7

WORKDIR /workspace/telegram_bot
COPY telegram_bot .
COPY rmq_manager /workspace/telegram_bot/rmq_manager

RUN pip install -e rmq_manager
