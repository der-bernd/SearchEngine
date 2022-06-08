# crawl a webpage and index all the links

import requests
from bs4 import BeautifulSoup
import sys

from mysql_connector import MySqlConnector

MAX_DEPTH = 2
START_URL = "https://www.google.com"

conn = MySqlConnector()

def add_link_to_db(link):
    does_link_already_exist = conn.execute_query("SELECT URL FROM links WHERE URL = '{}'".format(link)) != ()
    if not does_link_already_exist:
        conn.execute_query("INSERT INTO links (URL) VALUES ('{}')".format(link))
        print("Added link: {}".format(link))

def crawl_page(url, depth_left=0):
    if depth_left <= 0:
        return
    print("Crawling: {}".format(url))
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    for link in soup.find_all('a'):
        link = link.get('href')
        if link is not None:
            # make sure that the link is a valid url
            add_link_to_db(link.startswith('http') and link or url + link)

            if link.startswith('http'):
                crawl_page(link, depth_left-1)
            elif link.startswith('/'):
                crawl_page(url + link, depth_left-1)
            elif link.startswith('#'):
                continue
            else:
                crawl_page(url + '/' + link, depth_left-1)


def main():
    crawl_page(START_URL, MAX_DEPTH)


if __name__ == "__main__":
    main()
