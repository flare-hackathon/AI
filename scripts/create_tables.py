import sys
import os
import asyncio
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.db.models import Base
from app.db.session import engine

async def init():
    async with engine.begin() as conn:
        # Ensure pgvector extension exists before table creation
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init())
