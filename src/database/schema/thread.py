from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ══════════════════════════════════════════════════════════════════════════════
# MESSAGE
# ══════════════════════════════════════════════════════════════════════════════

class RoleEnum(str, Enum):
    # Role in LangChain Message
    human = "human"
    ai    = "ai"
    tool  = "tool"


class CitationSchema(BaseModel):
    """Single inline citation attached to an AI message."""
    article_id: UUID
    title:      str
    url:        str
    source:     Optional[str] = None
    score:      Optional[float] = Field(None, ge=0.0, le=1.0)


class MessageMeta(BaseModel):
    """
    Structured metadata stored in messages.meta (JSONB).
    All fields optional — only relevant ones are populated per message.
    """
    citations:  list[CitationSchema] = []
    tool_calls: list[dict[str, Any]] = []
    tokens:     Optional[dict[str, int]] = None   # {"prompt": 512, "completion": 128}


# ── Create ────────────────────────────────────────────────────────────────────
class MessageCreate(BaseModel):
    role:    RoleEnum = Field(..., examples=["human"])
    content: str      = Field(..., min_length=1)
    meta:    Optional[MessageMeta] = None


# ── Response ──────────────────────────────────────────────────────────────────
class MessageResponse(BaseModel):
    message_id: UUID
    thread_id:  UUID
    role:       RoleEnum
    content:    str
    meta:       Optional[MessageMeta] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ══════════════════════════════════════════════════════════════════════════════
# THREAD
# ══════════════════════════════════════════════════════════════════════════════

# ── Create ────────────────────────────────────────────────────────────────────
class ThreadCreate(BaseModel):
    """
    article_id=None → global RAG thread.
    article_id set  → per-article scoped thread.
    """
    user_id:    UUID
    article_id: Optional[UUID] = None


# ── Response ──────────────────────────────────────────────────────────────────
class ThreadResponse(BaseModel):
    thread_id:  UUID
    user_id:    UUID
    article_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Thread with full history ──────────────────────────────────────────────────
class ThreadWithMessages(ThreadResponse):
    messages: list[MessageResponse] = []

    model_config = {"from_attributes": True}


# ── QnA request (what the frontend sends) ─────────────────────────────────────
class QnARequest(BaseModel):
    """
    Single user question submitted from the chat UI.
    thread_id is optional on first message — backend creates thread if missing.
    """
    user_id:    UUID
    question:   str  = Field(..., min_length=1, max_length=2000)
    article_id: Optional[UUID] = None   # None → global RAG mode
    thread_id:  Optional[UUID] = None   # None → create new thread


class QnAResponse(BaseModel):
    thread_id: UUID
    message:   MessageResponse