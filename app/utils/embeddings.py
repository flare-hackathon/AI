#app/utils/embeddings.py
from langchain_ollama import OllamaEmbeddings
from typing import List
import logging
from app.config import OLLAMA_BASE_URL


# Configure your Ollama model name
OLLAMA_MODEL = "nomic-embed-text"


def get_post_embedding(title: str, content: str) -> List[float]:
    """
    Given a post's title and content, return a 768-dim embedding vector using nomic-embed-text via Ollama.
    Args:
        title (str): The post title
        content (str): The post content
    Returns:
        List[float]: Embedding vector (length depends on model, usually 768)
    Raises:
        RuntimeError: If embedding fails
    """
    try:
        text = f"{title}\n{content}"
        embedder = OllamaEmbeddings(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)
        embedding = embedder.embed_query(text)
        if not isinstance(embedding, list) or not all(isinstance(x, (float, int)) for x in embedding):
            raise ValueError("Embedding output is not a float vector.")
        return embedding
    except Exception as e:
        logging.error(f"Failed to generate embedding: {e}")
        raise RuntimeError(f"Embedding failed: {e}")
