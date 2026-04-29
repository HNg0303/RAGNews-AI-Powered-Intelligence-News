from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

from src.database.relational.session import AsyncSessionLocal
from src.services.rag import rag_service

rag_router = APIRouter(
    prefix="/rag",
    tags= ["rag"]
)

# Enable API to send a JSON Payload
class Request(BaseModel):
    question: str
    user_id: UUID
    article_id: Optional[str] = None

@rag_router.post("/chat")
async def invoke(request: Request):
    try:
        async with AsyncSessionLocal() as db:
            result = await rag_service.chat(db, request.user_id, request.question, request.article_id)
            await db.commit()
            return {
                **result,
                "status": 200
            }
    except Exception as e:
        return HTTPException(
            status_code = 500,
            detail = e
        )
    
# 1. Define how your JSON payload should look
class InsightRequest(BaseModel):
    user_id: UUID
    article_id: str

@rag_router.post("/insight")
async def invoke(request: InsightRequest): # 2. Use the model here
    try:
        async with AsyncSessionLocal() as db:
            # 3. Access the variables from the request object
            result = await rag_service.gather_insights(db, request.user_id, request.article_id)
            await db.commit()
            return {
                **result,
                "status": 200
            }
    except Exception as e:
        # Note: raise HTTPException instead of returning it
        raise HTTPException(
            status_code = 500,
            detail = str(e)
        )



