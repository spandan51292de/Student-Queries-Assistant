import logging
from typing import Optional
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse

from app.core.config import settings

logger = logging.getLogger(__name__)

class VectorStoreManager:
    _instance = None
    _client: Optional[QdrantClient] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorStoreManager, cls).__new__(cls)
        return cls._instance

    def get_client(self) -> QdrantClient:
        """Returns the active Qdrant client, initializing it if necessary."""
        if self._client is None:
            logger.info("Initializing Qdrant Vector DB Client...")
            try:
                self._client = QdrantClient(url=settings.VECTOR_DB_URL)
                self._client.get_collections()
                logger.info("Successfully connected to Qdrant.")
            except UnexpectedResponse as e:
                logger.error(f"Failed to connect to Qdrant: {e}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error initializing Qdrant: {e}")
                raise
        return self._client

    def ensure_collection(self, collection_name: str, vector_size: int = 3072):
        client = self.get_client()
        try:
            collections = client.get_collections().collections
            exists = any(c.name == collection_name for c in collections)
            
            if not exists:
                logger.info(f"Creating Qdrant collection: {collection_name}")
                from qdrant_client.http.models import VectorParams, Distance
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=vector_size, 
                        distance=Distance.COSINE
                    )
                )
        except Exception as e:
            logger.error(f"Error ensuring collection {collection_name}: {e}")
            raise

vector_store = VectorStoreManager()