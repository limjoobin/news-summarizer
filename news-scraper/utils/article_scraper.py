from typing import List, Tuple
import requests
import re
import random
import logging
import asyncio

from bs4 import BeautifulSoup

logger = logging.getLogger('article_scraper')

DELAY = 3
PARA_WORD_LIMIT = 15
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"}

def get_article(url: str) -> List[str]:
    """
        Scrapes the article at the URL for text in their <p> tags, corresponding to the paragraphs in the article.

        Parameters
        ----------
        url: str
            The URL to scrape
        
        Returns
        -------
        paragraphs: List[str]
            A list containing the text from the <p> tags in the article
    """
    try:
        page = requests.get(url, headers=headers, timeout=10)
    except requests.exceptions.ConnectionError as e:
        logger.error("Connection error: ", e)
        return []
    except requests.exceptions.Timeout:
        logger.error(f"Timeout when trying to scrape from: {url}")
        return []
    
    if page.ok:
        soup = BeautifulSoup(page.content, "html.parser")

        for element in soup.find_all(['script', 'style', 'aside', 'nav', 'header', 'footer']):
            element.decompose()

        paragraphs = soup.find_all(["p"])
        return paragraphs
    return []

def process_article(paragraphs: List[str]) -> List[str]:
    """
        Processes each paragraph in the article for easy downstream processing
        1. Removes repeated whitespaces
        2. Removes any links (beginning with http(s)://), because those are not useful for article information
        3. Replace straight quotes (", ') with curly quotes (”, ’) to avoid confusion with python strings
        4. Filter out paragraphs that are less than 20 words long. These do not carry much information, and 
           prevents random <p> tags from appearing in the results

        Parameters
        ----------
        paragraphs: List[str]
            A list containing the text in each <p> tag of the article
        
        Returns
        -------
        results: List[str]
            A list containing the processed text of each <p> tag   
    """
    results = []

    for p in paragraphs:
        p = p.get_text(strip=True)
        # Remove repeated whitespaces from the paragraph
        p = re.sub(r'\s+', ' ', p)

        # Remove any strings that start with http:// or https://
        p = re.sub(r"^https?://\S+", " ", p)

        # Replace "'" with "’".
        p = re.sub(r"'", "’", p)

        # Replace opening/closing quotes with curly quotes
        for i in range(p.count('"')//2+1) : 
            # Alternate between open and closing quotes
            p = p.replace(r'"', '“', 1)
            p = p.replace(r'"', '”', 1)
        
        # Filter out paragraphs that are less than 15 words long
        if p.count(" ") > PARA_WORD_LIMIT:
            results.append(p)

        if len(results) > 25:
            # only take the first 25 paragraphs, this prevents the article from getting way too long
            return results

    return results

async def scrape_article(url: str) -> Tuple[str, List[str]]:
    """
        Gets the text from each <p> tag in the article and processes it, and then sleeps for a while.
        This is to prevent repeated scrapes from the same website.

        Parameters
        ----------
        url: str
            The URL of the article

        Returns
        -------
        url, paragraphs: Tuple[str, List[str]]
            A tuple containing the URL, and a list of text from each <p> tag in the article
    """
    # get_article and process_article is synchronous
    paragraphs = get_article(url)
    paragraphs = process_article(paragraphs)
    
    await asyncio.sleep(DELAY * random.uniform(0.5, 1.5)) # In case we somehow end up scraping from the same website
    
    logger.info(f"Successfully scraped article for {url}")

    return url, paragraphs