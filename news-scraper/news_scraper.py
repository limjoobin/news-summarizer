import asyncio
import logging
import logging.config
import time
from typing import Annotated, AsyncGenerator

import orjson
from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
import uvicorn

from utils import get_google_news, scrape_article

logging.config.fileConfig('news_scraper_logging.conf', disable_existing_loggers=False)
logger = logging.getLogger('news-scraper')

app = FastAPI(title='news-scraper')

async def get_articles_by_query(query: str, limit: int) -> AsyncGenerator[str, None]: # think of a better name!
    """
        Gets the URLs of articles related to the query, and asynchronously scrape the articles to obtain their information.
        Returns an asynchronous generator that yields the json formatted string containing article details.

        Parameters
        ----------
        query: str
            The query to search articles on

        limit: int
            The maximum number of articles to return. This is so that the articles do not take too long to return as each scraping each article
            has a 5 second delay

        Yields
        -------
        result: str
            A JSON-formatted string representing a dictionary containing the url of the article and a list of <p> tags at each article.
    """
    logger.info(f"Started news scraping for \"{query}\"")
    start_time = time.time()

    urls = get_google_news(query)
    
    tasks = []
    count = 0
    # Asynchronously scrape each article at the url, as they arrive from the async generator from get_google_news
    async for url in urls:
        if count >= limit:
            break
        
        # Step 1: Asynchronously scrape the article at the URL
        task = asyncio.create_task(scrape_article(url))
        task_results = await task

        # Step 2: As these results from the scraping task arrive, yield them
        url, paragraphs = task_results
        tasks.append(task)
        if len(paragraphs) > 0:
            count += 1
            result = {
                        "url": url, 
                        "paragraphs": paragraphs
                    }
            # Format the dictionary into a json string
            output = orjson.dumps(result).decode("utf-8")
            yield output     

    logger.info(f"News scraping completed in {time.time() - start_time:.2f}s")

@app.get("/article-details")
async def get_article_details(search_query: Annotated[str, Query(min_length=1, max_length=50, pattern=r'^[a-zA-Z0-9\s\-_\,]+$')], # Allow only alphanumeric characters and '-', '_', ',' in the query
                            limit: Annotated[int, Query(gt=0)] = 3
            ):
    return StreamingResponse(get_articles_by_query(search_query, limit), media_type='application/json')

    

if __name__ == '__main__':
    uvicorn.run("news_scraper:app", 
                host="127.0.0.1",
                port=8001,
                proxy_headers=False,
                log_level="info",
                access_log=True,
                reload=False
                )