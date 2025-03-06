import gradio as gr
import requests

NEWS_SCRAPER_URL = "http://localhost:8000/article-details"


def search_query(query: str) -> str:
    search_params = {"search_query": query}
    # TODO: change this to httpx for streaming
    # TODO: see if it even makes sense to stream the output, since we need to pass the output as a whole into the summarizer
    resp = requests.get(NEWS_SCRAPER_URL, params=search_params)
    return resp.text

interface = gr.Interface(
    fn=search_query,
    inputs=["text"],
    outputs=["text"]
)

if __name__ == '__main__':
    interface.launch()