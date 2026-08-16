from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import SessionLocal

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Yields an async database session for the duration of the HTTP request.
    """
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()