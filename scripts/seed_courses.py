import asyncio
import sys
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

async def seed_courses():
    db_url = getattr(settings, "DATABASE_URL", None)
             
    if not db_url:
        print("❌ Error: Could not find the database URL in settings.")
        return
        
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif db_url.startswith("postgresql+psycopg2://"):
        db_url = db_url.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)
        
    print(f"Connecting to database with async driver...")
    
    engine = create_async_engine(db_url)
    
    async with engine.begin() as conn:
        await conn.execute(text("""
            INSERT INTO courses (id, code, title, description, created_at) 
            VALUES 
                (1, 'SE101', 'Software Engineering', 'Experiment 6 and System Architectures', NOW()),
                (2, 'ML201', 'Machine Learning', 'Transformers and LLMs', NOW())
            ON CONFLICT (id) DO NOTHING;
        """))
        
    print("✅ Courses successfully seeded into the database!")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed_courses())