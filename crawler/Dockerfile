ARG DB_HOST
ARG DB_USER
ARG DB_PASSWORD
ARG DB_NAME
FROM python:3.9-alpine

WORKDIR /crawler

EXPOSE 5001

COPY requirements.txt requirements.txt

RUN cat requirements.txt

RUN python -m pip install --upgrade pip

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]