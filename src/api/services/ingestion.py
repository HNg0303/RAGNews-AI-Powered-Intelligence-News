from fastapi import APIRouter, HTTPException
from src.services.ingestion import ingestion_service

ingestion_router = APIRouter(
    prefix="/ingestion",
    tags= ["ingestion"]
)

@ingestion_router.post("/")
async def invoke():
    try:
        await ingestion_service.index()
        return {
            "message": "Indexing successfully.",
            "status": "200"
        }
    except Exception as e:
        return HTTPException(
            status_code = 500,
            detail = e
        )



