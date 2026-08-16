import logging
import asyncio
import json
import ast
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
        ) if docs else "No course documents available."

        history_str = "No previous history."
        if past_messages:
            history_str = ""
            for msg in past_messages:
                role = "Student" if msg.sender == "user" else "Assistant"
                history_str += f"{role}: {msg.content}\n"

        system_prompt = f"""You are an expert AI Assistant helping students.
You are currently engaged in an ongoing conversation. Below is the chat history and the newly retrieved course context.

=== Chat History ===
{history_str}

=== Retrieved Course Context ===
{context_str}

=== Student's Current Question ===
{request.message}

INSTRUCTIONS:
1. Analyze the Chat History to understand if the Current Question is a follow-up (e.g., asking about "point 6", "this", "explain more").
2. If the question refers to something in the Chat History, use the history to understand the full context of what the student is asking.
3. Only use the Retrieved Course Context if it contains relevant facts for the actual intent of the question. If the Vector DB retrieved irrelevant context (e.g., pulling "Section 6" when the user meant "Point 6" from your previous message), IGNORE the Course Context and rely purely on the Chat History.

=== Answer ==="""

        raw_response = await asyncio.to_thread(default_llm.generate, system_prompt)
        
        answer_text = str(raw_response)
        
        if isinstance(raw_response, list) and len(raw_response) > 0:
            answer_text = raw_response[0].get("text", answer_text)
        elif isinstance(raw_response, str) and raw_response.strip().startswith("[{"):
            try:
                parsed_response = ast.literal_eval(raw_response)
                if isinstance(parsed_response, list) and len(parsed_response) > 0:
                    answer_text = parsed_response[0].get("text", answer_text)
            except (ValueError, SyntaxError):
                pass

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
        
        history_str = "No previous history."
        if past_messages:
            history_str = ""
            for msg in past_messages:
                role = "Student" if msg.sender == "user" else "Assistant"
                history_str += f"{role}: {msg.content}\n"
        
        system_prompt = f"""You are an expert AI Assistant helping students.
You are currently engaged in an ongoing conversation. Below is the chat history and the newly retrieved course context.

=== Chat History ===
{history_str}

=== Retrieved Course Context ===
{context_str}

=== Student's Current Question ===
{request.message}

INSTRUCTIONS:
1. Analyze the Chat History to understand if the Current Question is a follow-up (e.g., asking about "point 6", "this", "explain more").
2. If the question refers to something in the Chat History, use the history to understand the full context of what the student is asking.
3. Only use the Retrieved Course Context if it contains relevant facts for the actual intent of the question. If the Vector DB retrieved irrelevant context (e.g., pulling "Section 6" when the user meant "Point 6" from your previous message), IGNORE the Course Context and rely purely on the Chat History.

=== Answer ==="""

        full_answer = ""
        async for chunk in default_llm.astream(system_prompt):
            token_str = str(chunk)
            if isinstance(chunk, list) and len(chunk) > 0:
                token_str = chunk[0].get("text", "")
            elif isinstance(chunk, str) and chunk.strip().startswith("[{"):
                try:
                    parsed = ast.literal_eval(chunk)
                    if isinstance(parsed, list) and len(parsed) > 0:
                        token_str = parsed[0].get("text", "")
                except (ValueError, SyntaxError):
                    pass
                    
            full_answer += token_str
            token_payload = {"type": "token", "content": token_str}
            yield f"data: {json.dumps(token_payload)}\n\n"

        assistant_msg = Message(conversation_id=conversation.id, sender="assistant", content=full_answer)
        db.add(assistant_msg)
        await db.commit()

        yield f"data: {json.dumps({'type': 'done'})}\n\n"