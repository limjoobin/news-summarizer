import scrapy
from pathlib import Path

from scrapy.crawler import CrawlerProcess

CRAWLER_SETTINGS = {
            "FEEDS": {
                "items.json": {"format": "json"},
                "indent": 4,
            },
        }

class QuoteSpider(scrapy.Spider):
    name = 'quote-spider'

    def start_requests(self):
        urls = [
            'https://news.google.com/search?q=meta'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = f"quotes-{page}.html"
        Path(filename).write_bytes(response.body)
        self.log(f"Saved file {filename}")

if __name__ == '__main__':
    process = CrawlerProcess(
        settings=CRAWLER_SETTINGS
    )

    process.crawl(QuoteSpider)
    process.start()