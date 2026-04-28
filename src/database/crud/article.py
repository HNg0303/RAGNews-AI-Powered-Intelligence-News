from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID
import asyncio

from sqlalchemy import select, update, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert

from src.database.relational.models import Article
from src.database.schema.article import ArticleCreate, ArticleUpdate

# ══════════════════════════════════════════════════════════════════════════════
# ARTICLE
# ══════════════════════════════════════════════════════════════════════════════

async def create_article(db: AsyncSession, data: ArticleCreate) -> Article:
    article = Article(**data.model_dump(exclude_none=True))
    db.add(article)
    await db.flush()
    await db.refresh(article)
    return article

async def get_article(db: AsyncSession, article_id: str) -> Optional[Article]:
    result = await db.execute(
        select(Article).where(Article.article_id == article_id)
    )
    return result.scalar_one_or_none()

async def get_articles(db: AsyncSession, limit: int = 20) -> List[Optional[Article]]:
    result = await db.execute(
        select(Article)
        .where(Article.content.isnot(None))
        .limit(limit)
    )
    return list(result.scalars().all())

async def update_article(
    db: AsyncSession, article_id: str, data: ArticleUpdate
) -> Optional[Article]:
    article = await get_article(db, article_id)
    if not article:
        return None

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(article, field, value)

    await db.flush()
    await db.refresh(article)
    return article


async def save_summary(
    db: AsyncSession, article_id: str, summary: str
) -> None:
    """
    Called by the summarize_article agent tool after Gemini generates a summary.
    Lightweight update — only touches summary fields.
    """
    await db.execute(
        update(Article)
        .where(Article.article_id == article_id)
        .values(
            summary=summary,
            is_summarized=True,
            summarized_at=datetime.utcnow(),
        )
    )


async def get_unsummarized_articles(
    db: AsyncSession, limit: int = 20
) -> list[Article]:
    """Batch summarization job — find articles not yet summarized."""
    result = await db.execute(
        select(Article)
        .where(Article.is_summarized == False)  # noqa: E712
        .where(Article.content.isnot(None))
        .limit(limit)
    )
    return list(result.scalars().all())


async def delete_article(db: AsyncSession, article_id: str) -> bool:
    article = await get_article(db, article_id)
    if not article:
        return False
    await db.delete(article)
    await db.flush()
    return True