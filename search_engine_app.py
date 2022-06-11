# simple flask server to serve the search engine app

import time
from tokenize import String
import unittest
from flask import Flask, render_template, request, jsonify

from mysql_connector import MySqlConnector

mysql = MySqlConnector()
app = Flask(__name__)


def run():
    app.run(debug=True)


def format_diff_in_ms(diff: float) -> str:
    """
    Returns a string representation of the time difference in milliseconds.
    """
    return f"{diff:.2f} ms"


def count_word_in_pages(word: str) -> int:
    """
    Returns the number of pages that contain the word.
    """
    result = mysql.query(
        "SELECT COUNT(*) FROM links WHERE URL LIKE %s", (f"%{word}%", ))
    return int(result[0][0])


def get_urls_with_word(word: str) -> list:
    """
    Returns a list of URLs that contain the word.
    """
    result = mysql.query(
        "SELECT URL, TITLE FROM links WHERE URL LIKE %s", (f"%{word}%",))
    return [(row[0], row[1]) for row in result]


def get_list_of_occurrences(word: str, title_contain_factor: int, title_start_factor: int, title_match_factor: int, url_contain_factor: int) -> list:
    """
    Returns a list of tuples whether the word is in the title or url of the page
    """
    # at the moment, query returns all(!) pages in db, only adds the information whether they
    # contain the word in title or url

    # to reduce the amount of returned data, we could also embed a wh
    result = mysql.query(
        """WITH bools AS(
        SELECT ID,
        IF(LOWER(TITLE) LIKE %s, 1, 0) AS IS_IN_TITLE,
        IF(LOWER(TITLE) LIKE %s, 1, 0) AS IS_TITLE_START,
        IF(LOWER(TITLE) = 'google', 1, 0) AS IS_TITLE,
        IF(LOWER(URL) LIKE %s, 1, 0) AS IS_IN_URL
        FROM links
        WHERE LOWER(TITLE) LIKE %s OR LOWER(URL) LIKE %s
    )
    SELECT
        ID,
        TITLE,
        URL,
        bools.IS_IN_TITLE * %s + bools.IS_TITLE_START * %s + bools.IS_TITLE * %s + bools.IS_IN_URL * %s AS SCORE
        FROM bools
        JOIN LINKS USING(ID)
        ORDER BY SCORE DESC""", (f"%{word}%", f"{word}%", word, f"%{word}%", f"%{word}%",
                                 title_contain_factor, title_start_factor, title_match_factor, url_contain_factor))
    # param order: first one is just to contain in title, second is the title to start with the word,
    # third is the word itself as the title, fourth is the word in the url
    return [{
        "title": row[1],
        "url": row[2],
    } for row in result]


@app.route('/', methods=["GET"])
def search():
    return render_template('input_mask.html')


@app.route('/search', methods=["GET"])
def get_search_results():
    args = request.args
    query = args['query']
    first_word_of_query = query.split()[0]

    TITLE_CONTAIN_FACTOR = 2
    TITLE_START_FACTOR = 3
    TITLE_MATCH_FACTOR = 5
    URL_CONTAIN_FACTOR = 1

    start_time = time.time()

    # get the items and the info, whether title and whether url contains the word
    page_list_scored = get_list_of_occurrences(
        first_word_of_query, TITLE_CONTAIN_FACTOR, TITLE_START_FACTOR, TITLE_MATCH_FACTOR, URL_CONTAIN_FACTOR)

    end_time = time.time()
    elapsed_time = (end_time - start_time) * 1000

    return render_template('results.html', results={
        "pages": page_list_scored,
        "query": query,
        "stats": {
            "num_of_results": len(page_list_scored),
            "time": format_diff_in_ms(elapsed_time)
        }
    })


class Testing(unittest.TestCase):

    def test_lookup_word_in_pages(self):
        self.assertEqual(count_word_in_pages("?!ahhaajakkfnef?!"), 0)
        # hopefully this will fail

    def test_get_urls_with_word(self):
        self.assertEqual(get_urls_with_word("?!ahhaajakkfnef?!"), [])


if __name__ == '__main__':
    run()
    # unittest.main()
