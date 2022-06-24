# crawl a webpage and index all the links

from msilib.schema import Error
import time
import unittest
from urllib.parse import MAX_CACHE_SIZE
import requests
from bs4 import BeautifulSoup
import sys
import os
import json
import mysql.connector

from dotenv import load_dotenv

load_dotenv()

db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}

class Crawler:
    def __init__(self):
        
        conn = mysql.connector.connect(**db_config)
        if not conn.is_connected():
            raise Error(f"""Could not get cursors, probably because of a connection error.\n
            Are these credentials correct: {db_config}? E: {e}""")
        cursor = conn.cursor()
        print(f"Connection established with config {db_config}")


        
        cursor.execute("TRUNCATE links")
        cursor.execute("TRUNCATE spiders")

        print("Tables have been truncated")

        conn.commit()

        self.conn = conn


    def crawl(self, url: str, depth_left, interval: float = 5):
        """
        Crawl the page with the given url.
        If we cannot go further or no links should be crawled any more, return.
        Wait for the given interval before crawling.
        """
        if depth_left <= 0:
            return

        time.sleep(interval)
        print("Crawling: {}".format(url))

        # get the page
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        try:
            title = soup.title.text.strip().replace(
                "\n", " ").replace("\r", " ").replace("\t", " ")
        except AttributeError:
            title = "- No title -"

        # add the current page as well

        url = url.split("?")[0]
        self.add_link_to_db(url, title)

        # get the text content

        text_from_paragraphs = [p.text.strip() for p in soup.find_all("p")]
        print("Text from paragraphs: {}".format(text_from_paragraphs))

        for link in soup.find_all('a'):
            link = link.get('href')
            if link is not None:
                # cut off the param part of the url
                link = link.split("?")[0]

                if link.startswith('http'):
                    self.crawl(link, depth_left-1, interval)
                elif link.startswith('/'):
                    self.crawl(url + link, depth_left -
                               1, interval)
                elif link.startswith('#'):
                    continue
                else:
                    self.crawl(url + '/' + link, depth_left -
                               1, interval)

    def add_link_to_db(self, link: str, title: str):
        conn = self.conn
        cursor = conn.cursor()
        if not conn.is_connected():
            raise Error(f"""Could not establish conn again, probably because of a connection error.\n
            Are these credentials correct: {db_config}?""")
        cursor.execute(
            "SELECT COUNT(*) FROM links WHERE URL = %s", (link, ))
        does_link_already_exist = cursor.fetchall()[0][0] > 0
        print(does_link_already_exist)
        if not does_link_already_exist:
            cursor.execute(
                "INSERT INTO links (URL, TITLE) VALUES (%s, %s)", (link, title))
            conn.commit()
            print("Added link: {}".format(link))


class SimpleTest(unittest.TestCase):
    def test_add_to_db_and_query(self):
        conn = MySqlConnector()

        crawler = Crawler()
        # adding a link to the db which hasn't been there yet

        urls_to_be_added = [f"https://random.link/{i}" for i in range(10)]

        # add some links to the db
        for url in urls_to_be_added:
            crawler.add_link_to_db(url)

        urls_supposed_to_be_added = [
            "https://random2.link", "https://random.link/home"]
        urls_supposed_not_to_be_added = [
            "https://random.link?no", "https://random.link#no"]

        for url in urls_supposed_to_be_added + urls_supposed_to_be_added:
            crawler.add_link_to_db(url)

        # check if the right links were added and the wrong ones weren't
        # currently very dirty way of checking
        number_of_links_supposed_to_be_in_db = len(
            urls_to_be_added) + len(urls_supposed_to_be_added)
        links_in_db = conn.query("SELECT COUNT(*) FROM links")[0][0]

        # tidy up
        conn.query("DELETE FROM links", no_fetchall=True)

        self.assertEqual(number_of_links_supposed_to_be_in_db, links_in_db)


if __name__ == "__main__":
    unittest.main()
