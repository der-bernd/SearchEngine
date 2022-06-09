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


@app.route('/', methods=["GET"])
def search():
    return render_template('input_mask.html')


@app.route('/search', methods=["GET"])
def get_search_results():
    args = request.args
    query = args['query']
    first_word_of_query = query.split()[0]

    start_time = time.time()

    page_data = get_urls_with_word(first_word_of_query)

    end_time = time.time()
    elapsed_time = (end_time - start_time) * 1000

    urls_split = []
    for (url, title) in page_data:
        # split the text so it can be highlighted in results
        parts = url.split(first_word_of_query)
        urls_split.append((title, parts[0], first_word_of_query, parts[1]))

    return render_template('results.html', results={
        "pages": urls_split,
        "query": query,
        "stats": {
            "num_of_results": len(page_data),
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
