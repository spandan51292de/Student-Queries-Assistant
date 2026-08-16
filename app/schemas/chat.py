from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict

# Message Schemas
class MessageBase(BaseModel):
    sender: str
    content: str

class MessageCreate(MessageBase):
    conversation_id: int

class MessageResponse(MessageBase):
    id: int
    conversation_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Conversation Schemas
class ConversationResponse(BaseModel):
    id: int
    title: Optional[str]
    user_id: int
    course_id: Optional[int]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# RAG Query Request / Response
class ChatQueryRequest(BaseModel):
    message: str
    course_id: Optional[int] = None
    conversation_id: Optional[int] = None

class Citation(BaseModel):
    document_id: Optional[int] = None
    document_title: str
    snippet: str

class ChatQueryResponse(BaseModel):
    conversation_id: int
    answer: str
    citations: List[Citation] = []