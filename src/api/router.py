from fastapi import APIRouter
from src.api.articles.routers import article_router
from src.api.services.ingestion import ingestion_router
from src.api.services.rag import rag_router


routers = APIRouter()

routers.include_router(article_router)
routers.include_router(ingestion_router)
routers.include_router(rag_router)