from crawler import Crawler

MAX_DEPTH = 2
START_URL = "https://www.google.com"


if __name__ == "__main__":
    print("Ok, starting the crawler...")
    print(
        f"Config: max_depth={MAX_DEPTH}, start_url={START_URL}")
    crawler = Crawler()
    crawler.crawl(START_URL, MAX_DEPTH, 5)
    print("Done crawling!")
