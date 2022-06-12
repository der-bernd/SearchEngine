# simple flask server to serve the search engine app

from flask import send_from_directory
import time
from tokenize import String
import unittest
from flask import Flask, render_template, request, jsonify

from mysql_connector import MySqlConnector

mysql = MySqlConnector()
app = Flask(__name__)


@app.route('/static/<path:path>')
def send_report(path):
    return send_from_directory('static', path)


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


def calculate_score(is_in_title: int, is_title_start: int, is_title: int, is_in_url: int) -> int:
    """
    Calculates the score of a page.
    """
    TITLE_CONTAIN_FACTOR = 2
    TITLE_START_FACTOR = 3
    TITLE_MATCH_FACTOR = 5
    URL_CONTAIN_FACTOR = 1

    score = 0
    if is_in_title:
        score += is_in_title * TITLE_CONTAIN_FACTOR
    if is_title_start:
        score += is_title_start * TITLE_START_FACTOR
    if is_title:
        score += is_title * TITLE_MATCH_FACTOR
    if is_in_url:
        score += is_in_url * URL_CONTAIN_FACTOR

    return score


def get_list_of_occurrences(query_list: list[str]) -> list:
    """
    Returns a list of tuples whether the word is in the title or url of the page
    """
    # at the moment, query returns all(!) pages in db, only adds the information whether they
    # contain the word in title or url

    # it's important to use a dict here for O(1) access times
    results_of_keywords = {}
    for idx, word in enumerate(query_list):
        result = mysql.query(
            """SELECT ID,
            IF(LOWER(TITLE) LIKE %s, 1, 0) AS IS_IN_TITLE,
            IF(LOWER(TITLE) LIKE %s, 1, 0) AS IS_TITLE_START,
            IF(LOWER(TITLE) = %s, 1, 0) AS IS_TITLE,
            IF(LOWER(URL) LIKE %s, 1, 0) AS IS_IN_URL,
            TITLE,
            URL
            FROM links
            WHERE LOWER(TITLE) LIKE %s OR LOWER(URL) LIKE %s
            """, (f"%{word}%", f"{word}%", word, f"%{word}%", f"%{word}%", f"%{word}%",))
        # param order: first one is just to contain in title, second is the title to start with the word,
        # third is the word itself as the title, fourth is the word in the url
        # five and six are just for the where clause, to avoid returning all pages

        # for each element: add the score to the list
        for row in result:
            if row[0] not in results_of_keywords:
                # if page not in results yet, then accommodate it by initializing the dict
                for row in result:
                    # take the id as the index
                    results_of_keywords[row[0]] = {
                        "title": row[5],
                        "url": row[6],
                        "score": [],
                    }

            results_of_keywords[row[0]]["score"].append(
                calculate_score(row[1], row[2], row[3], row[4]))

    def multiply_scores(score_list: list) -> int:
        """
        Multiplies all scores in the list and returns the result.
        """
        result = 1
        for score in score_list:
            result *= score
        return result

    max_score = 0

    for result in results_of_keywords.values():
        # we have all the scores in an array, we could use the data to do a bit advanced stuff as well
        # but for now, just multiply them to have a bit more weight on pages with more keywords
        result["score"] = multiply_scores(result["score"])

        # and, if the score is higher than the max score, set it as the new max score
        if result["score"] > max_score:
            max_score = result["score"]

    rows_with_max_data = []
    # and transform the dict to a list of dicts, additionally adding the max score and the part of it
    for row in results_of_keywords.values():
        rows_with_max_data.append(
            row | {"max_score": max_score, "part_of_max_score": row["score"] / max_score})

    # sort the results by score
    rows_with_max_data = sorted(
        rows_with_max_data, key=lambda x: x["score"], reverse=True)
    return rows_with_max_data


@app.route('/', methods=["GET"])
def search():
    return render_template('index.html')


@app.route('/search', methods=["GET"])
def get_search_results():
    args = request.args
    query = args['query']
    query_list = query.split()

    start_time = time.time()

    # get the items and the info, whether title and whether url contains the word
    page_list_scored = get_list_of_occurrences(query_list)

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
    unittest.main()
