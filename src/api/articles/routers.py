from fastapi import APIRouter
from pydantic import BaseModel
import random
from typing import List
import json
import os
from pathlib import Path

from src.database.relational.session import AsyncSessionLocal
from src.database.relational.models import Article
from src.database.schema.article import ArticleCreate, ArticleUpdate
from src.database.crud.article import (
    get_article,
    get_articles
)

article_router = APIRouter(
    prefix="/article",
    tags=["article"]
)

# Enable FrontEnd to send query parameters
@article_router.get("/get_article/{article_id}")
async def get_article_by_id(article_id: str):
    async with AsyncSessionLocal() as db:
        article = await get_article(db = db, article_id=article_id)
        return article

@article_router.get("/get_articles")
async def get_multiple_articles(limit: int = 10):
    async with AsyncSessionLocal() as db:
        articles = await get_articles(db = db, limit = limit)
        return articles
    
    
