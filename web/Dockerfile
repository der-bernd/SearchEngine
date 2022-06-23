ARG DB_HOST
ARG DB_USER
ARG DB_PASSWORD
ARG DB_NAME
FROM python:3.9-alpine

WORKDIR /web

EXPOSE 5000

COPY . .

RUN pip install -r requirements.txt

CMD ["python", "main.py"]