import logging
from typing import List
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
from qdrant_client.models import VectorParams, Distance
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

class ContextRetriever:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.client = QdrantClient(url="http://localhost:6333")
        self.collection_name = "course_documents_hf"
        
        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )
        
        self.vectorstore = QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding=self.embeddings,
        )

    def retrieve(self, query: str, course_id: int = None, top_k: int = 4) -> List[Document]:
        logger.info(f"Retrieving context for query: '{query}' (course_id={course_id})")
        
        filter_kwargs = {}
        

        if course_id is not None:
            filter_kwargs["filter"] = qdrant_models.Filter(
                must=[
                    qdrant_models.FieldCondition(
                        key="metadata.course_id", 
                        match=qdrant_models.MatchValue(value=course_id)
                    )
                ]
            )

        docs = self.vectorstore.similarity_search(
            query=query,
            k=top_k,
            **filter_kwargs
        )
        
        logger.info(f"Retrieved {len(docs)} relevant chunks.")
        return docs