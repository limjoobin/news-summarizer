from typing import Generator

from pygooglenews import GoogleNews #TODO: find another way to search through google news without violating their robots.txt, and using
from googlenewsdecoder import new_decoderv1

gn = GoogleNews(lang = 'en', country = 'US')
INTERVAL_TIME = 5 # Recommended value to prevent rate limits

def get_google_news(query: str) -> Generator[str, None, None]:
    """
        Searches Google News (news.google.com) with a search query for related news in the past 1 hour and yields the url to the news articles

        Parameters
        ----------
        query: str
            The search query (use this as you would do a search in Google News)

        Returns
        -------
        Generator
            A generator that yields the url to the news articles
    """
    resp = gn.search(query, when = '1h', helper = True)['entries']
    count = 0
    for news in resp:
        count += 1
        if count == 3:
            break
        #print("Starting to decode ", news['link'])
        url = new_decoderv1(news['link'], interval= INTERVAL_TIME)
        #print("Finished decoding ",url)
        yield url['decoded_url']