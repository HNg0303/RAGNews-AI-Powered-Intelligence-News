from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# ── Base ──────────────────────────────────────────────────────────────────────
class UserBase(BaseModel):
    username: Optional[str] = Field(None, max_length=100, examples=["john_doe"])
    email:    Optional[EmailStr] = Field(None, examples=["john@example.com"])


# ── Create ────────────────────────────────────────────────────────────────────
class UserCreate(UserBase):
    """Used when registering a new user. Both fields optional for anonymous users."""
    pass


# ── Update ────────────────────────────────────────────────────────────────────
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, max_length=100)
    email:    Optional[EmailStr] = None


# ── Response ──────────────────────────────────────────────────────────────────
class UserResponse(UserBase):
    user_id:    UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# ── With Preferences (nested) ─────────────────────────────────────────────────
class UserWithPreferences(UserResponse):
    preferences: Optional["UserPreferencesResponse"] = None

    model_config = {"from_attributes": True}


# imported at bottom to avoid circular
from .user_preferences import UserPreferencesResponse  # noqa: E402
UserWithPreferences.model_rebuild()