import logging
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from langchain_huggingface import HuggingFaceEmbeddings

logger = logging.getLogger(__name__)

class IngestionPipeline:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
        
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

    def process_pdf(self, file_path: str, course_id: int = None, document_id: int = None) -> int:
        logger.info(f"Starting ingestion for file: {file_path}")
        
        try:
            loader = PyMuPDFLoader(file_path)
            docs = loader.load()
            
            logger.debug(f"PDF loaded successfully. Found {len(docs)} pages.")

            if docs and not docs[0].page_content.strip():
                logger.warning("WARNING: Page 1 is completely blank! If all pages are blank, this is a scanned image PDF.")

            chunks = self.text_splitter.split_documents(docs)
            logger.info(f"Split document into {len(chunks)} chunks.")

            if len(chunks) == 0:
                logger.error("No text could be extracted to chunk. Aborting ingestion.")
                return 0

            for chunk in chunks:
                if course_id is not None:
                    chunk.metadata["course_id"] = course_id
                if document_id is not None:
                    chunk.metadata["document_id"] = document_id
                
                file_name = file_path.replace("\\", "/").split("/")[-1]
                chunk.metadata["source"] = file_name

            self.vectorstore.add_documents(chunks)
            logger.info(f"Successfully ingested document {document_id} into Qdrant.")
            
            return len(chunks)

        except Exception as e:
            logger.error(f"Failed to process PDF {file_path}: {str(e)}")
            raise e