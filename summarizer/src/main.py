from typing import List, Dict

from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel

from openai import OpenAI

from utils import chunk_text

app = FastAPI()

# Attempt to load from a locally downloaded version of the model. If not found, download it from huggingface
#model_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "bart-large-cnn")
#model = model_dir if os.path.exists(model_dir) else "facebook/bart-large-cnn"
model = "bart-large-cnn"

openai_api_key = "EMPTY"
openai_api_base = "http://vllm-server:8000/v1"
client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)

class Article(BaseModel):
    url: str
    paragraphs: List[str]

def summarize_text(text: str):
    """
        Invokes the API at the vLLM server to summarize the text using the model served at the vLLM server.

        Parameters
        ----------
        text: str
            The text to summarize
        
        Returns
        -------
        response_text: str
            The summarized text
    """
    response = client.completions.create(model=model,
                                      prompt=f"Summarize: {text}",
                                      temperature=0.8, 
                                        top_p=0.95)
    response_text = response.choices[0].text.strip()
    return response_text

def get_summary(text: str) -> str:
    """
        Generates a summary for the article using the LLM. The article is first splits into chunks and each chunk 
        is summarized indepdently. Then, the summaries of each chunk is appended and returned as a single string.
        TODO: Maybe implement some post processing of the appended summary to ensure grammatical flow or something?

        Parameters
        ----------
        text: str
            The text to summarize

        Returns
        -------
        article_summary: str
            The summarized article
    """
    # Chunk the text such that the number of tokens fit within the token limits of the model
    chunks = chunk_text(text)

    # Get the output from the model
    article_summary = [summarize_text(chunk) for chunk in chunks]
    article_summary = " ".join(article_summary)

    return article_summary

@app.post("/article-summary")
async def summarize_article(article: Article) -> Dict[str, str]:
    """
        API endpoint to get the article summary as the response
        # TODO: INSTEAD OF USING FASTAPI, WHY NOT USE VLLM OPENAI-COMPATIBLE SERVER

        Parameters
        ----------
        article: Article
            The article details containing the url and a list of the <p> tags from the article HTML

        Returns
        -------
        response: Dict[str]
        A JSON response (converted to string type by FastAPI) containing the summarized article
        {
            "url": The url of the article
            "summary": The article summary
        }
    """
    paragraphs = article.paragraphs
    article_summary = get_summary(paragraphs)
    response = {
        "url": article.url,
        "summary": article_summary
        }
    
    return response

if __name__ == "__main__":
    uvicorn.run("main:app", 
                host="127.0.0.1",
                port=8002,
                proxy_headers=False,
                )