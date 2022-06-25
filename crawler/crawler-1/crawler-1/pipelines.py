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

load_dotenv()

class TutorialPipeline:
    def process_item(self, item, spider):
        return item


class SqlStorePipeline(object):

    def __init__(self):
        db_params = {
            "host": os.getenv("DB_HOST"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "database": os.getenv("DB_NAME")
        }

        conn = mysql.connector.connect(**db_params)
        if not conn.is_connected():
            raise RuntimeError(f"COULD NOT CONNECT TO DB with given config: {db_params}")

        self.conn = conn

    def process_item(self, item, spider):
        cleaned_words = []

        for word in item["text"].split():
            if word in stopword_set:
                continue
            cleaned_words.append(word)

        cursor = self.conn.cursor(buffered=True)

        cursor.execute("DELETE FROM spiders WHERE URL = %s", (item["url"],))

        try:
            cursor.execute("INSERT INTO spiders (URL, TITLE, TEXT, ESSENCE) VALUES (%s, %s, %s, %s)",
                                 (item["url"],  item["title"], item["text"], " ".join(cleaned_words)))
        except:
            # just in case the item is already in the DB though it shouldn't be
            pass

        cursor.close()
        self.conn.commit()


