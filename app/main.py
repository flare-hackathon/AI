# app/main.py
from fastapi import FastAPI
from app.scheduler import router as scheduler_router

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

# Register the scheduler routes
app.include_router(scheduler_router)