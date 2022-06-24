FROM python:3.9-alpine

ENV DB_HOST localhost
ENV DB_USER root
ENV DB_PASSWORD root

WORKDIR /web

EXPOSE 5000

COPY . .

RUN pip install -r requirements.txt

CMD ["python", "main.py"]