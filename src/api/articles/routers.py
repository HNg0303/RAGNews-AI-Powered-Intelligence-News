from fastapi import APIRouter
from pydantic import BaseModel
from src.schema.article import Article

import random
from typing import List
import json
import os
from pathlib import Path

ARTICLES_PATH = Path("data/raw_news/")

article_router = APIRouter(
    prefix="/article",
    tags=["article"]
)

@article_router.get("/get_article/{article_id}")
async def get_article(article_id: str, response_model = Article):
    # Current local storage
    article_path =  ARTICLES_PATH / article_id
    with open(f"{str(article_path)}.json", "r", encoding = "utf-8") as f:
        article = json.load(f)
    return {
        "id": article["id"],
        "title": article["title"],
        "content": article["content"],
        "source": article["source"] if "source" in article else ""
    }

@article_router.get("/get_articles")
async def get_articles(response_model = List[Article]):
    def load_all_articles():
        articles = []
        if not ARTICLES_PATH.exists():
            # demo fallback if directory is missing entirely
            return _demo_articles()

        # walk recursively to include subfolders like CNN/, APNews/, etc.
        for files in ARTICLES_PATH.iterdir():
            try:
                with open(files, encoding="utf-8") as fp:
                    articles.append(json.load(fp))
            except Exception:
                continue

        return articles if articles else _demo_articles()
    def _demo_articles():
        return [
            {
                "id": "demo-001",
                "title": "'Golden' wins K-pop's first Grammy. Is this a breakthrough moment? | CNN",
                "content": (
                    "Golden was already a global chart-dominating force, but taking home the "
                    "Best Song Written for Visual Media award in Los Angeles is a milestone moment "
                    "for K-pop – a genre that despite its growing influence on Western pop culture "
                    "has long been considered niche.\n\n"
                    "\"It does feel so miraculous in some ways. And destined in other ways…\" said "
                    "Audrey Nuna, who lends her voice to a member of Huntr/x in the film.\n\n"
                    "The Grammy itself went to the songwriters: EJAE, Park Hong Jun, Joong Gyu Kwak, "
                    "Yu Han Lee, Hee Dong Nam, Seo Jeong Hoon and Mark Sonnenblick – the first win "
                    "for any Korean songwriters or producers.\n\n"
                    "It was only in 2021 that a K-pop act first earned a Grammy nomination. "
                    "This year, songs released by K-pop artists received nominations in five categories."
                ),
            }
        ]

    articles = load_all_articles()
    random.shuffle(articles)
    return [
        Article(
            id=art["id"],
            title=art["title"],
            content=art["content"],
            source=art["source"] if "source" in art else ""
        ) for art in articles[:7]
    ]
    
