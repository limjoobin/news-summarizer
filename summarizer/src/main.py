from typing import List, Dict
import os

from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel
from transformers import AutoTokenizer
from vllm import LLM, SamplingParams

from utils import chunk_text

app = FastAPI()

# Attempt to load from a locally downloaded version of the model. If not found, download it from huggingface
model_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "bart-large-cnn")
model = model_dir if os.path.exists(model_dir) else "facebook/bart-large-cnn"
llm = LLM(model=model, 
          gpu_memory_utilization=0.7
        )
tokenizer = AutoTokenizer.from_pretrained(model)

sampling_params = SamplingParams(
                                temperature=0.8, 
                                top_p=0.95,
                                max_tokens=1024
                            )

class Article(BaseModel):
    url: str
    paragraphs: List[str]

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
    chunks = chunk_text(text, tokenizer)

    # Get the summary of the chunk from the model (Do we need this if using bart?)
    prompts = [f"Summarize: {chunk}" for chunk in chunks]
    summarizer_output = llm.generate(prompts, sampling_params)

    # Get the output from the model
    article_summary = [output.outputs[0].text for output in summarizer_output]
    article_summary = " ".join(article_summary)

    return article_summary

@app.post("/article-summary")
async def summarize_article(article: Article) -> Dict[str]:
    """
        API endpoint to get the article summary as the response

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