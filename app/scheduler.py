# app/scheduler.py
from fastapi import APIRouter
from app.services.scorer import score_new_posts
from app.db.session import AsyncSessionLocal
import asyncio

router = APIRouter()

@router.post("/trigger-scoring")
async def trigger_scoring():
    async def background_task():
        async with AsyncSessionLocal() as session:
            await score_new_posts(session)

    asyncio.create_task(background_task())
    return {"status": "Scoring started"}
