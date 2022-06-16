# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json
import os
import mysql.connector

import nltk
from itemadapter import ItemAdapter
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
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "host": os.getenv("DB_HOST"),
            "database": os.getenv("DB_NAME")
        }
        print(db_params)
        self.db = mysql.connector.connect(**db_params)

        self.db.cursor().execute("TRUNCATE TABLE spider")

        self.db.commit()

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
