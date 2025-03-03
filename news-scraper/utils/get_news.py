from typing import AsyncGenerator
import asyncio
import logging

from pygooglenews import GoogleNews #TODO: find another way to search through google news without violating their robots.txt (try: bing news api?)
from googlenewsdecoder import new_decoderv1

logger = logging.getLogger('get_news')

gn = GoogleNews(lang = 'en', country = 'US')
INTERVAL_TIME = 5 # Recommended value to prevent rate limits

async def get_google_news(query: str) -> AsyncGenerator[str, None]:
    """
        Searches Google News (news.google.com) with a search query for related news in the past 1 day and yields the url to the news articles

        Parameters
        ----------
        query: str
            The search query (use this as you would do a search in Google News)

        Returns
        -------
        Generator
            A generator that yields the url to the news articles
    """
    resp = gn.search(query, when = '1d', helper = True)['entries']
    #print(gn.search(query, when = '1d', helper = True))
    for count, news in enumerate(resp):
        
        #if count == 3: break
        #title = news['title']
        #published_time = news['published_parsed']
        #google_url = news['link']
        url = await decode_news_async(news)
        logger.info(f"Obtained URL {url}")
        yield url

async def decode_news_async(news: str):
    """
        Decode the google news url (rss) to the url of the actual news article, in an async thread to ensure the INTERVAL_TIME is respected

        Parameters
        ----------
        news: str
            The url of the news article from google news
        
        Returns
        -------
        decoded_url: str
            The url of the actual news article
    """
    result = await asyncio.to_thread(new_decoderv1, news['link'], interval= INTERVAL_TIME) 
    decoded_url = result['decoded_url']
    return decoded_url