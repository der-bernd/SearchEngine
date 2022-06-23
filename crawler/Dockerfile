ARG DB_HOST
ARG DB_USER
ARG DB_PASSWORD
ARG DB_NAME
FROM python:3.9-slim-bullseye

WORKDIR /crawler

EXPOSE 5001

RUN python -m venv /opt/venv

COPY requirements.txt .

RUN . /opt/venv/bin/activate && pip install -r requirements.txt

RUN . /opt/venv/bin/activate && pip freeze

COPY . .

CMD . /opt/venv/bin/activate && exec python main.py