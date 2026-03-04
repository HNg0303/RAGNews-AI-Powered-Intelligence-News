from fastapi import APIRouter
from src.api.articles.routers import article_router


routers = APIRouter()

routers.include_router(article_router)