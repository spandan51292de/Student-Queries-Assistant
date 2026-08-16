from abc import ABC, abstractmethod
from typing import List

class BaseLLM(ABC):
    """Abstract base class for Language Models."""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate a response based on a prompt."""
        pass

class BaseEmbeddings(ABC):
    """Abstract base class for Text Embeddings."""
    
    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of document chunks."""
        pass

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """Embed a single search query."""
        pass