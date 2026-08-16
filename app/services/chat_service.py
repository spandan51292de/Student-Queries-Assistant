import logging
import asyncio
import json
from typing import List, AsyncGenerator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.conversation import Conversation
from app.db.models.message import Message
from app.llm import default_llm
from app.rag.retriever import ContextRetriever
from app.schemas.chat import ChatQueryRequest, ChatQueryResponse, Citation

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        self.retriever = ContextRetriever()

    async def process_query(
        self, db: AsyncSession, user_id: int, request: ChatQueryRequest
    ) -> ChatQueryResponse:
        """Process a query and return the full response asynchronously."""
        
        if request.conversation_id:
            result = await db.execute(
                select(Conversation).filter(
                    Conversation.id == request.conversation_id,
                    Conversation.user_id == user_id
                )
            )
            conversation = result.scalars().first()
            if not conversation:
                conversation = Conversation(
                    user_id=user_id, course_id=request.course_id, title=request.message[:50]
                )
                db.add(conversation)
        else:
            conversation = Conversation(
                user_id=user_id, course_id=request.course_id, title=request.message[:50]
            )
            db.add(conversation)
            
        await db.flush()

        result = await db.execute(
            select(Message).filter(
                Message.conversation_id == conversation.id
            ).order_by(Message.created_at.desc()).limit(6)
        )
        past_messages = list(result.scalars().all())
        past_messages.reverse()

        user_msg = Message(
            conversation_id=conversation.id, sender="user", content=request.message
        )
        db.add(user_msg)
        await db.flush()

        docs = await asyncio.to_thread(
            self.retriever.retrieve, query=request.message, course_id=request.course_id, top_k=4
        )

        context_str = "\n\n".join(
            [f"--- Context Chunk {i+1} ---\n{doc.page_content}" for i, doc in enumerate(docs)]
        ) if docs else "No course documents available for this context."

        history_str = ""
        if past_messages:
            history_str = "=== Chat History ===\n"
            for msg in past_messages:
                role = "Student" if msg.sender == "user" else "Assistant"
                history_str += f"{role}: {msg.content}\n"
            history_str += "\n"

        system_prompt = f"""You are an expert AI Assistant helping students.
Use the provided course context below to accurately answer the student's current question.

{history_str}=== Course Context ===
{context_str}

=== Student's Current Question ===
{request.message}

=== Answer ==="""

        answer_text = await asyncio.to_thread(default_llm.generate, system_prompt)

        assistant_msg = Message(
            conversation_id=conversation.id, sender="assistant", content=answer_text
        )
        db.add(assistant_msg)
        await db.commit()

        citations = [
            Citation(
                document_id=doc.metadata.get("document_id"),
                document_title=doc.metadata.get("source", "Course Document"),
                snippet=doc.page_content[:200] + "..."
            ) for doc in docs
        ]

        return ChatQueryResponse(
            conversation_id=conversation.id, answer=answer_text, citations=citations
        )

    async def stream_query(
        self, db: AsyncSession, user_id: int, request: ChatQueryRequest
    ) -> AsyncGenerator[str, None]:
        """Process a query and stream the response back using Server-Sent Events (SSE)."""
        
        if request.conversation_id:
            result = await db.execute(
                select(Conversation).filter(
                    Conversation.id == request.conversation_id,
                    Conversation.user_id == user_id
                )
            )
            conversation = result.scalars().first()
            if not conversation:
                conversation = Conversation(
                    user_id=user_id, course_id=request.course_id, title=request.message[:50]
                )
                db.add(conversation)
        else:
            conversation = Conversation(
                user_id=user_id, course_id=request.course_id, title=request.message[:50]
            )
            db.add(conversation)
            
        await db.flush()

        result = await db.execute(
            select(Message).filter(Message.conversation_id == conversation.id)
            .order_by(Message.created_at.desc()).limit(6)
        )
        past_messages = list(result.scalars().all())
        past_messages.reverse()

        user_msg = Message(conversation_id=conversation.id, sender="user", content=request.message)
        db.add(user_msg)
        await db.flush()

        docs = await asyncio.to_thread(
            self.retriever.retrieve, query=request.message, course_id=request.course_id, top_k=4
        )

        citations = [
            {
                "document_id": doc.metadata.get("document_id"),
                "document_title": doc.metadata.get("source", "Course Document"),
                "snippet": doc.page_content[:200] + "..."
            } for doc in docs
        ]
        
        meta_payload = {
            "type": "metadata",
            "conversation_id": conversation.id,
            "citations": citations
        }
        yield f"data: {json.dumps(meta_payload)}\n\n"

        context_str = "\n\n".join([f"--- Chunk {i+1} ---\n{doc.page_content}" for i, doc in enumerate(docs)])
        history_str = "".join([f"{'Student' if m.sender == 'user' else 'Assistant'}: {m.content}\n" for m in past_messages])
        
        system_prompt = f"""You are an expert AI Assistant helping students.
Use the provided course context below to accurately answer the student's current question.

=== Chat History ===
{history_str}
=== Course Context ===
{context_str}

=== Student's Current Question ===
{request.message}

=== Answer ==="""

        full_answer = ""
        async for token in default_llm.astream(system_prompt):
            full_answer += token
            token_payload = {"type": "token", "content": token}
            yield f"data: {json.dumps(token_payload)}\n\n"

        assistant_msg = Message(conversation_id=conversation.id, sender="assistant", content=full_answer)
        db.add(assistant_msg)
        await db.commit()

        yield f"data: {json.dumps({'type': 'done'})}\n\n"