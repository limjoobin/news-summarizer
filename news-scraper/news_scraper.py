import asyncio
import logging
import logging.config
import time
from typing import Annotated

from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
import uvicorn

from utils import get_google_news, scrape_article

logging.config.fileConfig('news_scraper_logging.conf')
logger = logging.getLogger('news-scraper')

app = FastAPI(title='news-scraper')

async def get_articles_by_query(query: str): # think of a better name!
    logger.info(f"Started news scraping for \"{query}\"")
    start_time = time.time()

    urls = get_google_news(query)
    tasks = []

    async for url in urls:
        task = asyncio.create_task(scrape_article(url))
        tasks.append(task)

    for task in asyncio.as_completed(tasks):
        article_details = await task  
        yield article_details.encode("utf-8") 

    logger.info(f"News scraping completed in {time.time() - start_time:.2f}s")

@app.get("/article-details")
async def get_article_details(search_query: Annotated[
                        str, Query(min_length=1, max_length=50, pattern=r'^[a-zA-Z0-9\s\-_\,]+$') # Allow only alphanumeric characters and '-', '_', ',' in the query
            ]):
    return StreamingResponse(get_articles_by_query(search_query), media_type='text/plain')

            
if __name__ == '__main__':
    uvicorn.run("news_scraper:app", 
                reload=True, # DISABLE THIS IN PRODUCTION
                proxy_headers=False,
                )