FROM python:3.9-slim-bullseye

ENV DB_HOST localhost
ENV DB_USER root
ENV DB_PASSWORD root

WORKDIR /crawler

RUN python -m venv /opt/venv

COPY requirements.txt .

RUN . /opt/venv/bin/activate && pip install -r requirements.txt

COPY . .

CMD . /opt/venv/bin/activate && cd crawler-1 && exec scrapy crawl simplespider
