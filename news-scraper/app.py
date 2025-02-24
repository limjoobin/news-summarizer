import asyncio
import logging
import logging.config
import time

from utils import get_google_news, scrape_article

logging.config.fileConfig('news_scraper_logging.conf')
logger = logging.getLogger('news-scraper')

async def main(query):
    urls = get_google_news(query)
    tasks = []
    async with asyncio.TaskGroup() as tg:
        #tasks = [tg.create_task(scrape_article(url)) async for url in urls]
        async for url in urls: 
            task = tg.create_task(scrape_article(url))
            tasks.append(task)
    return [task.result() for task in tasks]
            
if __name__ == '__main__':
    query = 'covid 19'
    logger.info(f"Started news scraping for \"{query}\"")
    start_time = time.time()
    res = asyncio.run(main(query))
    print(res)
    logger.info(f"News scraping completed in {time.time() - start_time:.2f}s")


