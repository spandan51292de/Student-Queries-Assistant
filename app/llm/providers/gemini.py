from typing import List, AsyncGenerator
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

from app.core.config import settings
from app.llm.base import BaseLLM, BaseEmbeddings

class GeminiLLM(BaseLLM):
    def __init__(self, model_name: str = "gemini-3.6-flash", temperature: float = 0.0):
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            google_api_key=settings.GOOGLE_API_KEY
        )

    def generate(self, prompt: str, **kwargs) -> str:
        response = self.llm.invoke(prompt, **kwargs)
        return str(response.content)

    async def astream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """Asynchronously streams chunks of the generated response."""
        async for chunk in self.llm.astream(prompt, **kwargs):
            yield chunk.content

class GeminiEmbeddingProvider(BaseEmbeddings):
    def __init__(self, model_name: str = "models/gemini-embedding-001"):
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=model_name,
            google_api_key=settings.GOOGLE_API_KEY
        )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.embeddings.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        return self.embeddings.embed_query(text)