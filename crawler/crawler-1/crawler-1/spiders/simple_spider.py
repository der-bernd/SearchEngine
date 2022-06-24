import scrapy


class SimpleSpider(scrapy.Spider):
    name = "simplespider"

    start_urls = [
        'https://en.wikipedia.org/wiki/Search_engine',
        "https://www.alwego.de/",
        "https://en.wikipedia.org/wiki/Special:Random"
        "https://en.wikipedia.org/wiki/Special:Random"
        "https://en.wikipedia.org/wiki/Special:Random"
    ]

    custom_settings = {
        "DEPTH_LIMIT": 2
    }

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = f'saved-pages/simplespider-{page}.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log(f'Saved file {filename}')

        for next_page in response.xpath('//a/@href').extract():
            if "?" in next_page:
                # If ? is in the url, it's more likely a web-app
                # Currently easiest solution: just do not crawl it
                continue

            yield response.follow(next_page, callback=self.parse)

        # all text nodes, except those which are in: head, scripts, styles, links, buttons
        # ref: https://stackoverflow.com/a/36535089
        xpath = '//text()[not(ancestor::script | ancestor::style | ancestor::head)]'
        xpath = '//p/text()'

        title_xpath = '//title/text()'

        title = response.xpath(title_xpath).extract_first() or None

        all_ps = "".join(response.xpath(xpath).extract())
        all_ps = all_ps.replace("\n", " ").replace(
            "\r", " ").replace("\t", " ").lower()

        try:
            yield {
                'url': response.url,
                'text': all_ps,
                "title": title
            }
        except:
            pass
