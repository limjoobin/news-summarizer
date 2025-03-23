from __future__ import annotations
from typing import List

# TODO: maybe instead of setting hard limits for the chunks, try to decide it based on the average number of chunks in each paragraph.
CHUNK_TOKEN_LIMIT = 200
CHUNK_OVERLAP = 2
MAX_PARA_IN_CHUNK = CHUNK_OVERLAP * 2 + 1 # To prevent too many paragraphs being in the same chunk, resulting in loss of information post summarization

def count_text_tokens(text: str, tokenizer: transformers.AutoTokenizer) -> int:
    """
        Counts the number of tokens in the text.

        Parameters
        ---------
        text: str
            The text from which you want the token counts
        
        tokenizer: transformers.AutoTokenizer
            The tokenizer used to tokenize the text
        
        Returns
        -------
        num_tokens: int
            The number of tokens in the text
    """
    tokens = tokenizer.encode(text, add_special_tokens=False)  # Encode without special tokens
    num_tokens = len(tokens)
    return num_tokens

def chunk_text(text: str, tokenizer: transformers.AutoTokenizer) -> List[str]:
    """
        Chunks the article text to make it easier to summarize, and for the text to fit within the token limit of the summarizer.
        This ensures that the text passed into the summarizer is not too long, and will not result in loss of information post summarization
        if the generated summary is too short.

        The chunking strategy used is a sentence-aware(?) rolling window. 
        1. The number of tokens in each paragraph (of the article) is obtained.
        2. Add each paragraph to the chunk until the total number of tokens in that chunk exceeds CHUNK_TOKEN_LIMIT, or if the number of paragraphs
           in the chunk exceeds MAX_PARA_IN_CHUNK. This attempts to find a nice balance in the length of the chunk and the amount of information 
           present in the chunk, so that not too much information will be lost due to the summarization.
        3. If the current chunk is filled, take the last CHUNK_OVERLAP paragraphs as the start of the new chunk. Repeat step 2 until all the chunks
           have been obtained

        Parameters
        ----------
        text: str
            The article text to chunk

        tokenizer: transformers.AutoTokenizer
            The tokenizer used to tokenize the text
        
        Returns
        -------
        chunks: List[str]
            A list of chunked text created from the article
    """   
    text_tokens = [count_text_tokens(t, tokenizer) for t in text]

    chunks = []
    current_chunk = []
    token_count = 0
    for i, (paragraph_text, num_tokens) in enumerate(zip(text, text_tokens)):
        if token_count + num_tokens >= CHUNK_TOKEN_LIMIT or len(current_chunk) >= MAX_PARA_IN_CHUNK:
            # End of current_chunk
            chunks.append(" ".join(current_chunk))

            # Form the beginning of the new current_chunk using the previous paragraphs
            window_start_idx = max(i-CHUNK_OVERLAP, 0)
            current_chunk = text[window_start_idx:i] 
            token_count = sum(text_tokens[window_start_idx:i])

        current_chunk.append(paragraph_text)
        token_count += num_tokens

    # Add the final chunk
    if current_chunk: # do we need this check?
        chunks.append(" ".join(current_chunk))
    return chunks