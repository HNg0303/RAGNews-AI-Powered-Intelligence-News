from fastapi import APIRouter
from pydantic import BaseModel
from src.schema.article import Article

from typing import Annotated, Literal
import json

ARTICLES_PATH = "data/raw_news/"

article_router = APIRouter(
    prefix="/article",
    tags=["article"]
)

@article_router.get("/get_article/{article_id}")
async def get_article(article_id: str, response_model = Article):
    # Current local storage
    article_path =  ARTICLES_PATH + article_id
    with open(article_path, "r", encoding = "utf-8") as f:
        article = json.load(f)

    return {
        "title": article["title"],
        "content": article["content"],
        "source": article["source"]
    }