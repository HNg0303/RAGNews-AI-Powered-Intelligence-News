from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

from src.database.relational.session import db
from src.services.rag import rag_service

rag_router = APIRouter(
    prefix="/rag",
    tags= ["rag"]
)

class Request(BaseModel):
    question: str
    user_id: UUID
    article_id: Optional[UUID] = None

@rag_router.post("/")
async def invoke(question: str, user_id: UUID, article_id: Optional[UUID] = None):
    try:
        result = await rag_service.chat(db, user_id, question, article_id)
        return {
            **result,
            "status": "200"
        }
    except Exception as e:
        return HTTPException(
            status_code = 500,
            detail = e
        )



