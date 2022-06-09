from crawler import Crawler

MAX_DEPTH = 2
START_URL = "https://www.google.com"
MAX_LINKS_TO_CRAWL = 5


if __name__ == "__main__":
    print("Ok, starting the crawler...")
    print(
        f"Config: max_depth={MAX_DEPTH}, start_url={START_URL}, max_links_to_crawl={MAX_LINKS_TO_CRAWL}")
    crawler = Crawler()
    crawler.crawl(START_URL, MAX_DEPTH, MAX_LINKS_TO_CRAWL, 5)
    print("Done crawling!")
