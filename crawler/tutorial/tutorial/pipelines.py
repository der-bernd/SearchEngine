# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json
import os
import mysql.connector

import nltk
from nltk.corpus import stopwords

from dotenv import load_dotenv

nltk.download("stopwords")

stopword_set = set(stopwords.words('english'))


class TutorialPipeline:
    def process_item(self, item, spider):
        return item


class SqlStorePipeline(object):

    def __init__(self):
        load_dotenv()
        db_params = {
            "host": os.getenv("DB_HOST"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "database": os.getenv("DB_NAME")
        }
        print(db_params)

        db = mysql.connector.connect(**db_params)
        cursor = db.cursor(buffered=True)
        if cursor is None:
            raise RuntimeError(f"COULD NOT CONNECT TO DB with given config: {db_params}")

        cursor.execute("TRUNCATE TABLE spider")

        cursor.commit()
        self.cursor = cursor

    def process_item(self, item, spider):
        cleaned_words = []

        for word in item["text"].split():
            if word in stopword_set:
                continue
            cleaned_words.append(word)

        "".join(cleaned_words)

        self.db.cursor().execute("INSERT INTO spider (URL, TITLE, TEXT, ESSENCE) VALUES (%s, %s, %s, %s)",
                                 (item["url"],  item["title"], item["text"], " ".join(cleaned_words)))

        self.db.commit()

        print({
            "url": item["url"],
            "text": " ".join(cleaned_words),
            "title": item["title"]
        })
