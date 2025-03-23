import asyncio
import urllib.parse
from typing import Dict, AsyncGenerator

import orjson
import httpx
import gradio as gr

#NEWS_SCRAPER_URL = "http://localhost:8001/article-details"
#SUMMARIZER_URL = "http://localhost:8002/article-summary"

NEWS_SCRAPER_URL = "http://news-scraper:8000/article-details"
SUMMARIZER_URL = "http://summarizer:8000/article-summary"

async def get_stream_from_news_scraper(query: str, limit: int) -> AsyncGenerator[Dict[str, str], None]:
    """
        Obtains a stream of articles from the news scraping service.

        Parameters
        ----------
        query: str
            To query the news service on

        limit: int
            The max number of articles to return

        Yields
        ------
        line: Dict[str]
        The response from the news scraping service. A dictionary containing the url and the <p> tags from the article
        {
            "url": The url of the article
            "paragraphs": A list containing the <p> tags from the article
        }
    """
    search_params = {"search_query": query,
                     "limit": limit}

    async with httpx.AsyncClient(timeout=None) as client:
        # TODO: implement a timeout for get_articles_by_query
        async with client.stream("GET", NEWS_SCRAPER_URL, params=search_params) as response:
            async for line in response.aiter_text():
                line = orjson.loads(line)
                yield line

async def get_news_summary(line: Dict[str, str]):
    """
        Passes the article (containing its url and a list of <p> text) to the summarizer service and returns the response

        Parameters
        ----------
        line: Dict
            A dictionary containing two keys, url and paragraphs
            {
                "url": url of the article
                "paragraphs": List[str] containing the text from all the <p> tags in the article
            }

        Returns
        -------
        response: Dict[str, str]
            A dictionary containing the response from the summarizer servicce
            {
                "url": url of the article
                "summary": Summary of the article
            }
    """
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.post(SUMMARIZER_URL, 
                                 json={
                                        "url": line['url'],
                                        "paragraphs": line['paragraphs']
                                    }
                                )
    # if resp = 200 ok?
    return response.json() 

def format_markdown_article(i: int, url: str, summary: str):
    """
        Formats the article summary into a markdown format to be displayed in gradio

        Parameters
        ----------
        i: int
            The id of the article
        url: str
            The url of the article
        summary: str
            The article summary
        
        Returns
        -------
        s: str
            The formatted markdown string.
    """
    # TODO: MAKE THIS LOOK NICER
    url = urllib.parse.quote(url, safe=":/?&=")
    s = f"""
## Article {i} <span style="font-size:12px">[🔗[link]({url})]</span> <br>
{summary}
    """
    return s

async def search_query(query: str, limit: int, progress = gr.Progress()) -> str:
    """
        Obtain the summaries of all the articles associated with the query, and formats them in output format for
        display on the gradio interface.
        TODO: maybe implement a database layer to collect article summaries 

        Parameters
        ----------
        query: str
            The query to articles on
        
        limit: int
            The max number of articles to collect. Collecting each article comes with a 5 second delay (for scraping purposes), 
            so there will be significant latency if too many articles are scraped in the same time

        Returns
        -------
        markdown_output: str
        The markdown output of all the article summaries
    """
    progress(0, "Getting Article Details")
    summaries = []
    count = 0

    # Obtain the article summaries
    async with asyncio.TaskGroup() as tg:
        async for line in get_stream_from_news_scraper(query, limit):
            task = tg.create_task(get_news_summary(line))

            task.add_done_callback(lambda x: summaries.append(x.result()))
            progress((count, limit), "Summarizing articles", unit="articles")
            count += 1

    # Format the article summaries to markdown
    markdown_output = [f"# Summary for articles related to <u>{query}</u>"]
    for i, article_summary in progress.tqdm(enumerate(summaries), "Formatting Summaries"):
        url = article_summary['url']
        summary = article_summary['summary']
        markdown_summary = format_markdown_article(i+1, url, summary)
        markdown_output.append(markdown_summary)

    return "\n___\n".join(markdown_output)

async def search_query_async(query, limit):
    # TODO: FIND A WAY TO MAKE GRADIO RENDER AND DISPLAY THE OUTPUT DYNAMICALLY AND ASYNCHRONOUSLY
    tasks = []
    async for line in get_stream_from_news_scraper(query, limit):
        task = asyncio.create_task(get_news_summary(line))
        tasks.append(task)
    
    for task in asyncio.as_completed(tasks):
        result = await task
        yield result

with gr.Blocks() as interface:
    query_output = gr.State({})
    filled = gr.State(1)
    tabs_text = []
    with gr.Row():
        with gr.Column(scale=1):
            input_query = gr.Textbox(label="Query")
            num_queries = gr.Number(value=1, 
                                    label="Number of summaries to get", 
                                    show_label=True, 
                                    precision=0,
                                    minimum=1
                                    )
            submit_btn = gr.Button("Submit", variant="primary")
            
        with gr.Column(scale=2) as c:
            summaries = gr.Markdown("# Summary",
                                    min_height=250, 
                                    max_height="90vh", 
                                    container=True)
            
        submit_btn.click(search_query, inputs=[input_query, num_queries], outputs=summaries) 

if __name__ == '__main__':
    interface.launch()