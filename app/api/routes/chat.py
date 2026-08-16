from typing import List
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.auth.dependencies import get_current_user
from app.db.models.user import User
from app.db.models.conversation import Conversation
from app.schemas.chat import ChatQueryRequest, ChatQueryResponse, ConversationResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["Chat & RAG"])
chat_service = ChatService()

@router.post("/query", response_model=ChatQueryResponse)
async def query_rag(
    request: ChatQueryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await chat_service.process_query(
        db=db, user_id=current_user.id, request=request
    )

@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Conversation).filter(
            Conversation.user_id == current_user.id
        ).order_by(Conversation.created_at.desc())
    )
    return result.scalars().all()

@router.post("/stream")
async def stream_rag(
    request: ChatQueryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit a query and stream the response back in real-time.
    Uses Server-Sent Events (SSE) format.
    """
    return StreamingResponse(
        chat_service.stream_query(db=db, user_id=current_user.id, request=request),
        media_type="text/event-stream"
    )