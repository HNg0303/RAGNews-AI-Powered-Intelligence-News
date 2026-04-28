from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ══════════════════════════════════════════════════════════════════════════════
# USER INTERACTION
# ══════════════════════════════════════════════════════════════════════════════

class InteractionEnum(str, Enum): 
    # Choices using Enum Class
    click = "click"
    qna   = "qna"
    share = "share"


# ── Create ────────────────────────────────────────────────────────────────────
class UserInteractionCreate(BaseModel):
    """
    Logged silently on frontend events.
    Fire-and-forget — never blocks the UI response.
    """
    user_id:     UUID
    article_id:  UUID
    interaction: InteractionEnum


# ── Response ──────────────────────────────────────────────────────────────────
class UserInteractionResponse(UserInteractionCreate):
    id:         UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Aggregated weight (used internally by personalization service) ─────────────
class ArticleWeight(BaseModel):
    article_id: UUID
    weight:     float   # qna=2, share=1.5, click=1 — summed across all events


# ══════════════════════════════════════════════════════════════════════════════
# USER PREFERENCES
# ══════════════════════════════════════════════════════════════════════════════

# ── Create / Upsert ───────────────────────────────────────────────────────────
class UserPreferencesUpsert(BaseModel):
    """
    Computed by the personalization service and written back to DB.
    Not called directly by the frontend.
    """
    category_weights: dict[str, float] = Field(
        default_factory=dict,
        examples=[{"technology": 0.8, "finance": 0.3}],
    )


# ── Response ──────────────────────────────────────────────────────────────────
class UserPreferencesResponse(BaseModel):
    user_id:          UUID
    category_weights: dict[str, float]
    # interest_vector intentionally excluded — never send 768-dim vector to frontend
    updated_at:       datetime
    model_config = {"from_attributes": True}