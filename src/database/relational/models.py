import uuid
from datetime import datetime
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from .session import Base
"""
ORM Models for RAGNews
─────────────────────
Tables:
  users               → user accounts
  articles            → full content, summary, sentiment
  threads             → one per article (scoped QnA) + one global per user
  messages            → LangChain-compatible conversation history
  user_interactions   → click / qna / share events (personalization signal)
  user_preferences    → aggregated category weights + pgvector interest vector
"""

# ── Helpers ───────────────────────────────────────────────────────────────────
def _uuid():
    return str(uuid.uuid4())


def _now():
    return datetime.utcnow()

# ═════════════════════════════════════════════════════════════════════════════
# USER
# ═════════════════════════════════════════════════════════════════════════════
class User(Base):
    __tablename__ = "users"

    user_id    = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username   = Column(String(100), unique=True, nullable=True)
    email      = Column(Text, unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # relationships
    preferences  = relationship("UserPreferences", back_populates="user", uselist=False)
    interactions = relationship("UserInteraction", back_populates="user")
    threads      = relationship("Thread", back_populates="user")

    def __repr__(self):
        return f"<User {self.username or self.user_id}>"

# ═════════════════════════════════════════════════════════════════════════════
# ARTICLE  (heavy — fetched only when user opens an article)
# ═════════════════════════════════════════════════════════════════════════════
class Article(Base):
    __tablename__ = "articles"

    article_id     = Column(Text, primary_key=True)
    title          = Column(Text, nullable=False)
    subtitle       = Column(Text, nullable=True)
    content        = Column(Text, nullable=True)
    image_url      = Column(Text, nullable=True)            # Cloudinary CDN URL
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # ── Summarization (lazy — populated by summarize_article tool) ──
    summary        = Column(Text, nullable=True)
    is_summarized  = Column(Boolean, default=False)
    summarized_at  = Column(DateTime(timezone=True), nullable=True)

    # ── Sentiment ──
    sentiment      = Column(String(20), nullable=True)      # positive | neutral | negative
    sentiment_score = Column(Float, nullable=True)          # confidence 0.0–1.0

    def __repr__(self):
        return f"<Article {self.title[:60] if self.title else self.article_id}>"


# ═════════════════════════════════════════════════════════════════════════════
# THREAD  (one per article per user + one global per user)
# ═════════════════════════════════════════════════════════════════════════════
class Thread(Base):
    __tablename__ = "threads"
    __table_args__ = (
        # Each user can have at most one global thread (article_id IS NULL)
        # and one thread per article — enforced at app layer, not DB constraint,
        # because NULL != NULL in SQL unique indexes. Use a partial index instead:
        #   CREATE UNIQUE INDEX ON threads (user_id) WHERE article_id IS NULL;
        # (See init.sql for the raw DDL version)
    )

    thread_id  = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id    = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"))
    article_id = Column(
        Text,
        ForeignKey("articles.article_id", ondelete="CASCADE"),
        nullable=True,   # NULL → global RAG thread
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # relationships
    user     = relationship("User", back_populates="threads")
    messages = relationship("Message", back_populates="thread", cascade="all, delete-orphan")

    def __repr__(self):
        scope = f"article={self.article_id}" if self.article_id else "global"
        return f"<Thread {scope} user={self.user_id}>"


# ═════════════════════════════════════════════════════════════════════════════
# MESSAGE  (LangChain-compatible conversation history)
# ═════════════════════════════════════════════════════════════════════════════
class Message(Base):
    __tablename__ = "messages"

    message_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    thread_id  = Column(
        UUID(as_uuid=True),
        ForeignKey("threads.thread_id", ondelete="CASCADE"),
        nullable=False,
    )
    role       = Column(String(20), nullable=False)  # "human" | "ai" | "tool"
    content    = Column(Text, nullable=False)

    # Flexible metadata: citations, source chunks, tool call details, token counts
    meta       = Column(JSONB, nullable=True)
    # Example meta shape:
    # {
    #   "citations": [{"article_id": "...", "title": "...", "url": "...", "score": 0.91}],
    #   "tool_calls": [{"name": "retrieve_all_docs", "input": {...}}],
    #   "tokens": {"prompt": 512, "completion": 128}
    # }

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # relationship
    thread = relationship("Thread", back_populates="messages")

    def __repr__(self):
        return f"<Message role={self.role} thread={self.thread_id}>"


# ═════════════════════════════════════════════════════════════════════════════
# USER INTERACTION  (raw event log — source of truth for personalization)
# ═════════════════════════════════════════════════════════════════════════════
class UserInteraction(Base):
    __tablename__ = "user_interactions"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id     = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"))
    article_id  = Column(Text, ForeignKey("articles.article_id", ondelete="CASCADE"))
    interaction = Column(String(20), nullable=False)   # "click" | "qna" | "share"
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    # relationship
    user = relationship("User", back_populates="interactions")

    def __repr__(self):
        return f"<UserInteraction {self.interaction} user={self.user_id}>"


# ═════════════════════════════════════════════════════════════════════════════
# USER PREFERENCES  (aggregated — refreshed async after each interaction)
# ═════════════════════════════════════════════════════════════════════════════
class UserPreferences(Base):
    __tablename__ = "user_preferences"

    user_id          = Column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        primary_key=True,
    )
    # {"technology": 0.8, "finance": 0.3, "sports": 0.1}
    category_weights = Column(JSONB, nullable=True, default=dict)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # relationship
    user = relationship("User", back_populates="preferences")

    def __repr__(self):
        return f"<UserPreferences user={self.user_id}>"