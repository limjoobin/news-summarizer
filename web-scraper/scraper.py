import scrapy
from pathlib import Path

from scrapy.crawler import CrawlerProcess
from scraper.spiders.news_spider import NewsSpider

CRAWLER_SETTINGS = {
            "FEEDS": {
                "items.json": {"format": "json"},
            },
        }



if __name__ == '__main__':
    process = CrawlerProcess(
        settings=CRAWLER_SETTINGS
    )

    process.crawl(NewsSpider, query='ukraine')
    process.start()