from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

class DocumentChunker:
    """Splits large documents into smaller overlapping chunks for vectorization."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 100):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False
        )

    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Takes a list of documents and returns a larger list of smaller chunked documents."""
        return self.text_splitter.split_documents(documents)