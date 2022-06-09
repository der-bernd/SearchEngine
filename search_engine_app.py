# simple flask server to serve the search engine app

from distutils.command.build_scripts import first_line_re
from tokenize import String
import unittest
from flask import Flask, render_template, request, jsonify

from mysql_connector import MySqlConnector

mysql = MySqlConnector()
app = Flask(__name__)


def run():
    app.run(debug=True)


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
        "SELECT URL FROM links WHERE URL LIKE %s", (f"%{word}%", ))
    return [row[0] for row in result]


@app.route('/', methods=["GET"])
def search():
    return render_template('input_mask.html')


@app.route('/search', methods=["GET"])
def get_search_results():
    args = request.args
    query = args['query']
    first_word_of_query = query.split()[0]
    print(query)
    search_results = [{
        "url": url,
        "title": "Google",
    } for url in get_urls_with_word(first_word_of_query)]

    return render_template('results.html', results={
        "pages": search_results,
        "search": query
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
