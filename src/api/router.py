from fastapi import APIRouter
from src.api.articles.routers import article_router
from src.api.images.routers import image_router
from src.api.agent.router import agent_router


routers = APIRouter()

routers.include_router(article_router)
routers.include_router(image_router)
routers.include_router(agent_router)