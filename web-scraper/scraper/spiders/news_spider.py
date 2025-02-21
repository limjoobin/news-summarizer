from pathlib import Path

import scrapy


class NewsSpider(scrapy.Spider):
    name = 'news-spider'

    def __init__(self, query=None, *args, **kwargs):
        super(NewsSpider, self).__init__(*args, **kwargs)
        self.search_query = f'https://news.google.com/search?q={query}'

    def start_requests(self):
        req = scrapy.Request(url=self.search_query, callback=self.parse)
        yield req

    def parse(self, response):
        if response.status != 200:
            pass # Error handling?

        page = response.url.split("/")[-2]
        filename = f"quotes-{page}.html"
        #out = response.css("body c-wiz main div c-wiz a::attr(href)").getall()
        out = response.css("article a::attr(href)").getall()

        count = 0
        
        for url in out:
            article = url.replace("\n", "").split("/")[-1]
            url = f"https://news.google.com/read/{article}"
            import time
            time.sleep(1)
            count += 1
            if count == 5: exit()
            yield scrapy.Request(url=url, callback = self.parse_article)
            #Path(filename).write_text(url + "\n")
        #

    def parse_article(self, response):
        # TODO: HANDLE FOR REDIRECT 302 (and possibly http 429)
        page = response.url.split("/")[-2]
        filename = f"quotes-{page}.html"
        Path(filename).write_bytes(response.status)
        self.log(f"Saved file {filename}")