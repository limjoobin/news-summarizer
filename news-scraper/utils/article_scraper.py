from typing import List
from bs4 import BeautifulSoup
import requests
import random
import re
import logging
import asyncio

logger = logging.getLogger('article_scraper')

DELAY = 3
PARA_WORD_LIMIT = 20
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"}

def process_article(paragraphs: List[str]):
    results = []
    for p in paragraphs:
        p = p.get_text(strip=True)

        # Remove repeated whitespaces from the paragraph
        p = re.sub(r'\s+', ' ', p).split(" ")

        # Filter out paragraphs that are less than 20 words long, they may not carry much information. This is to prevent random <p> tags from appearing in the results
        if len(p) > PARA_WORD_LIMIT:
            results.append(" ".join(p))
    return results

def get_article(url: str):
    try:
        page = requests.get(url, headers = headers)
    except requests.exceptions.ConnectionError as e:
        logger.error("Connection error: ", e)
        return []
    
    if page.ok:
        soup = BeautifulSoup(page.content, "html.parser")
        article = soup.find("article")
        if article:
            for element in article.find_all(['script', 'style', 'aside', 'nav', 'header', 'footer']):
                element.decompose()
            paragraphs = article.find_all("p")
            return paragraphs
    return []

async def scrape_article(url: str):
    # get_article and process_article is synchronous
    paragraphs = get_article(url)
    paragraphs = process_article(paragraphs)
    logger.info(f"Successfully scraped article for {url}")
    await asyncio.sleep(DELAY * random.uniform(0.5, 1.5)) # In case we somehow end up scraping from the same website

    return paragraphs