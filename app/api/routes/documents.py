from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, BackgroundTasks, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.auth.dependencies import get_current_user
from app.db.models.user import User
from app.db.models.document import Document
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    course_id: Optional[int] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to upload course materials."
        )

    db_doc = await DocumentService.save_upload_file(file=file, db=db, course_id=course_id)

    background_tasks.add_task(
        DocumentService.process_ingestion_background,
        document_id=db_doc.id,
        file_path=db_doc.file_path,
        course_id=course_id
    )

    return {
        "message": f"File '{file.filename}' received and queued for processing.",
        "document_id": db_doc.id,
        "status": db_doc.status
    }

@router.get("/{document_id}/status")
async def get_document_status(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Document).filter(Document.id == document_id))
    doc = result.scalars().first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found."
        )
    return {
        "document_id": doc.id,
        "title": doc.title,
        "status": doc.status,
        "error_message": doc.error_message,
        "created_at": doc.created_at
    }