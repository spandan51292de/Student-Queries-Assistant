import os
import asyncio
import logging
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.document import Document
from app.ingestion.pipeline import IngestionPipeline

logger = logging.getLogger(__name__)

UPLOAD_DIR = "data/raw"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class DocumentService:
    @staticmethod
    async def save_upload_file(file: UploadFile, db: AsyncSession, course_id: int = None) -> Document:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Currently, only PDF files are supported."
            )

        file_path = os.path.join(UPLOAD_DIR, file.filename)
        
        try:
            content = await file.read()
            
            def write_file():
                with open(file_path, "wb") as f:
                    f.write(content)
            
            await asyncio.to_thread(write_file)
            
        except Exception as e:
            logger.error(f"Failed to save file {file.filename}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not save the uploaded file to disk."
            )

        db_doc = Document(
            title=file.filename,
            file_path=file_path,
            file_type=file.content_type or "application/pdf",
            course_id=course_id,
            status="PENDING"
        )
        db.add(db_doc)
        await db.commit()
        await db.refresh(db_doc)
        return db_doc

    @staticmethod
    async def process_ingestion_background(document_id: int, file_path: str, course_id: int = None):
        try:
            def run_pipeline():
                pipeline = IngestionPipeline()
                return pipeline.process_pdf(file_path=file_path, course_id=course_id, document_id=document_id)

            chunks_added = await asyncio.to_thread(run_pipeline)
            logger.info(f"Ingestion succeeded for document {document_id}: {chunks_added} chunks added.")
            
        except Exception as e:
            logger.error(f"Ingestion failed for document {document_id}: {e}")