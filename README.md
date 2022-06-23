# Introduction

This project was to solve a task provided by a lesson named Database Programming Interfaces. The goal was to develop a simple search engine with a crawler which crawls title, url and most important words of a page (do stopword elimination).

# Run the stuff

As of now, the app consists of two components:

1. The Crawler, written in python
2. The Frontend/App, implemented as a HTML template which will be served via Python Framework Flask.
3. The DB which will be used to CRUD the results.

To run the crawler, just hop into the backend/tutorial/ dir and run the spider named _simplespider_ via the command

```
scrapy crawl simplespider

```
