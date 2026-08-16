from app.llm.base import BaseLLM, BaseEmbeddings
from app.llm.providers.gemini import GeminiLLM, GeminiEmbeddingProvider

default_llm = GeminiLLM()
default_embeddings = GeminiEmbeddingProvider()

__all__ = ["BaseLLM", "BaseEmbeddings", "default_llm", "default_embeddings"]