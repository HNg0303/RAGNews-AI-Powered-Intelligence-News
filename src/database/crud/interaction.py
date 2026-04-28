import numpy as np
from typing import Optional
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import UserInteraction, UserPreferences, ArticleLink
from schemas.user_preferences import (
    UserInteractionCreate,
    UserPreferencesUpsert,
    ArticleWeight,
)


# ══════════════════════════════════════════════════════════════════════════════
# USER INTERACTION
# ══════════════════════════════════════════════════════════════════════════════

async def log_interaction(
    db: AsyncSession, data: UserInteractionCreate
) -> UserInteraction:
    """
    Log a user event. Call this in a BackgroundTask — never block the response.

    After logging, trigger update_interest_vector() asynchronously.
    """
    interaction = UserInteraction(**data.model_dump())
    db.add(interaction)
    await db.flush()
    await db.refresh(interaction)
    return interaction


async def get_interactions_by_user(
    db: AsyncSession,
    user_id: UUID,
    limit: int = 100,
) -> list[UserInteraction]:
    result = await db.execute(
        select(UserInteraction)
        .where(UserInteraction.user_id == user_id)
        .order_by(UserInteraction.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_weighted_articles(
    db: AsyncSession,
    user_id: UUID,
    top_n: int = 20,
) -> list[ArticleWeight]:
    """
    Aggregate interaction events into weighted article scores.
    qna=2, share=1.5, click=1 — matches v_user_article_weights view logic.
    Used by update_interest_vector() to compute the mean embedding.
    """
    rows = await db.execute(
        text("""
            SELECT
                article_id,
                SUM(CASE
                    WHEN interaction = 'qna'   THEN 2.0
                    WHEN interaction = 'share' THEN 1.5
                    ELSE 1.0
                END) AS weight
            FROM user_interactions
            WHERE user_id = :user_id
            GROUP BY article_id
            ORDER BY weight DESC
            LIMIT :top_n
        """),
        {"user_id": str(user_id), "top_n": top_n},
    )
    return [
        ArticleWeight(article_id=row.article_id, weight=row.weight)
        for row in rows
    ]


async def get_interaction_count(db: AsyncSession, user_id: UUID) -> int:
    """Check if user has enough data for personalization (cold-start guard)."""
    result = await db.execute(
        select(UserInteraction)
        .where(UserInteraction.user_id == user_id)
    )
    return len(result.scalars().all())


# ══════════════════════════════════════════════════════════════════════════════
# USER PREFERENCES
# ══════════════════════════════════════════════════════════════════════════════

async def get_user_preferences(
    db: AsyncSession, user_id: UUID
) -> Optional[UserPreferences]:
    result = await db.execute(
        select(UserPreferences).where(UserPreferences.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def upsert_user_preferences(
    db: AsyncSession,
    user_id: UUID,
    data: UserPreferencesUpsert,
) -> UserPreferences:
    """
    Insert or update preferences in one query.
    Called by update_interest_vector() after every interaction.
    """
    values = {
        "user_id": user_id,
        "category_weights": data.category_weights,
        "interest_vector": data.interest_vector,
    }
    stmt = (
        pg_insert(UserPreferences)
        .values(**values)
        .on_conflict_do_update(
            index_elements=["user_id"],
            set_={
                "category_weights": data.category_weights,
                "interest_vector": data.interest_vector,
                "updated_at": text("NOW()"),
            },
        )
        .returning(UserPreferences)
    )
    result = await db.execute(stmt)
    await db.flush()
    return result.scalar_one()


async def update_interest_vector(
    db: AsyncSession, user_id: UUID
) -> Optional[UserPreferences]:
    """
    Full personalization recompute pipeline:
      1. Fetch weighted article list from interaction log
      2. Fetch article-level embeddings from article_links (pgvector column)
      3. Compute weighted mean → new interest_vector
      4. Recompute category_weights from interaction counts
      5. Upsert into user_preferences

    Call this in a background task after every log_interaction().
    Requires MIN_INTERACTIONS_FOR_PERSONALIZATION interactions (cold-start guard).
    """
    MIN_INTERACTIONS = 3

    total = await get_interaction_count(db, user_id)
    if total < MIN_INTERACTIONS:
        return None   # not enough data yet — use default feed

    # Step 1: weighted article list
    weighted = await get_weighted_articles(db, user_id, top_n=20)
    if not weighted:
        return None

    article_ids = [str(w.article_id) for w in weighted]
    weight_map  = {str(w.article_id): w.weight for w in weighted}

    # Step 2: fetch embeddings from pgvector column
    rows = await db.execute(
        select(ArticleLink.article_id, ArticleLink.embedding, ArticleLink.category)
        .where(ArticleLink.article_id.in_(article_ids))
        .where(ArticleLink.embedding.isnot(None))
    )
    rows = rows.all()

    if not rows:
        return None

    # Step 3: weighted mean embedding
    vectors = np.array([np.array(row.embedding) for row in rows])
    weights = np.array([weight_map.get(str(row.article_id), 1.0) for row in rows])
    weights = weights / weights.sum()           # normalize
    interest_vector = (vectors * weights[:, np.newaxis]).sum(axis=0)

    # Step 4: category weights (fraction of weighted interactions per category)
    category_totals: dict[str, float] = {}
    for row in rows:
        if row.category:
            w = weight_map.get(str(row.article_id), 1.0)
            category_totals[row.category] = category_totals.get(row.category, 0) + w

    total_weight = sum(category_totals.values()) or 1.0
    category_weights = {k: round(v / total_weight, 4) for k, v in category_totals.items()}

    # Step 5: upsert
    return await upsert_user_preferences(
        db,
        user_id,
        UserPreferencesUpsert(
            category_weights=category_weights,
            interest_vector=interest_vector.tolist(),
        ),
    )


async def get_personalized_feed(
    db: AsyncSession,
    user_id: UUID,
    days: int = 3,
    limit: int = 20,
) -> list[dict]:
    """
    pgvector cosine similarity between user interest_vector and article embeddings.
    Falls back to recency-based feed if user has no interest_vector yet.
    """
    from datetime import datetime, timedelta

    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()

    prefs = await get_user_preferences(db, user_id)

    if not prefs or prefs.interest_vector is None:
        # Cold-start: return newest articles
        rows = await db.execute(
            text("""
                SELECT
                    al.article_id, al.article_url, al.category,
                    al.source, al.published_at,
                    a.title, a.subtitle, a.image_url,
                    a.sentiment, a.sentiment_score, a.is_summarized,
                    NULL::float AS relevance_score
                FROM article_links al
                JOIN articles a ON al.article_id = a.article_id
                WHERE al.is_scraped = TRUE
                  AND al.published_at >= :cutoff
                ORDER BY al.published_at DESC
                LIMIT :limit
            """),
            {"cutoff": cutoff, "limit": limit},
        )
    else:
        # Personalized: cosine similarity via pgvector <=> operator
        rows = await db.execute(
            text("""
                SELECT
                    al.article_id, al.article_url, al.category,
                    al.source, al.published_at,
                    a.title, a.subtitle, a.image_url,
                    a.sentiment, a.sentiment_score, a.is_summarized,
                    1 - (al.embedding <=> CAST(:vector AS vector)) AS relevance_score
                FROM article_links al
                JOIN articles a ON al.article_id = a.article_id
                CROSS JOIN user_preferences up
                WHERE al.is_scraped = TRUE
                  AND al.published_at >= :cutoff
                  AND al.embedding IS NOT NULL
                  AND up.user_id = :user_id
                ORDER BY relevance_score DESC
                LIMIT :limit
            """),
            {
                "vector": str(prefs.interest_vector),
                "user_id": str(user_id),
                "cutoff": cutoff,
                "limit": limit,
            },
        )

    return [dict(row._mapping) for row in rows.all()]