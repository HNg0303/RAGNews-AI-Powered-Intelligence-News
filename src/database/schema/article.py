from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SentimentEnum(str, Enum):
    positive = "positive"
    neutral  = "neutral"
    negative = "negative"


# ── Base ──────────────────────────────────────────────────────────────────────
class ArticleBase(BaseModel):
    title:    str            = Field(..., examples=["Fed Holds Rates Steady"])
    subtitle: Optional[str] = None
    content:  Optional[str] = None
    image_url: Optional[str] = None


# ── Create ────────────────────────────────────────────────────────────────────
class ArticleCreate(ArticleBase):
    """
    Used by ingestion pipeline after scraping full content.
    article_id must match an existing article_links row.
    """
    article_id:      str
    sentiment:       Optional[SentimentEnum] = None
    sentiment_score: Optional[float]         = Field(None, ge=0.0, le=1.0)
    created_at: datetime


# ── Update ────────────────────────────────────────────────────────────────────
class ArticleUpdate(BaseModel):
    title:           Optional[str]           = None
    subtitle:        Optional[str]           = None
    content:         Optional[str]           = None
    image_url:       Optional[str]           = None
    summary:         Optional[str]           = None
    is_summarized:   Optional[bool]          = None
    sentiment:       Optional[SentimentEnum] = None
    sentiment_score: Optional[float]         = Field(None, ge=0.0, le=1.0)


# ── Response ──────────────────────────────────────────────────────────────────
class ArticleResponse(ArticleBase):
    article_id:      str
    summary:         Optional[str]
    is_summarized:   bool
    summarized_at:   Optional[datetime]
    sentiment:       Optional[SentimentEnum]
    sentiment_score: Optional[float]

    model_config = {"from_attributes": True}


# ── Full article page (join with ArticleLink metadata) ────────────────────────
class ArticleDetail(ArticleResponse):
    """Full article page response — joins ArticleLink fields."""
    article_url:  str
    category:     Optional[str]
    source:       Optional[str]
    published_at: Optional[datetime]

    model_config = {"from_attributes": True}