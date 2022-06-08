# simple flask server to serve the search engine app

from flask import Flask, render_template, request, jsonify


app = Flask(__name__)

@app.route('/', methods=["GET"])
def search():
    return render_template('input_mask.html')

@app.route('/search', methods=["GET", "POST"])
def get_search_results():
    results = [dict(
        title = "Hello",
        url = "https://example.com"
    ) for i in range(10)]
    return render_template('results.html', results=results)

app.run(debug=True)
