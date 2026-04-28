from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database.relational.models import Message, Thread
from src.database.schema.thread import MessageCreate, ThreadCreate


# ══════════════════════════════════════════════════════════════════════════════
# THREAD
# ══════════════════════════════════════════════════════════════════════════════

async def create_thread(db: AsyncSession, data: ThreadCreate) -> Thread:
    thread = Thread(**data.model_dump(exclude_none=True))
    db.add(thread)
    await db.flush()
    await db.refresh(thread)
    return thread


async def get_thread(db: AsyncSession, thread_id: UUID) -> Optional[Thread]:
    result = await db.execute(
        select(Thread).where(Thread.thread_id == thread_id)
    )
    return result.scalar_one_or_none()


async def get_thread_with_messages(
    db: AsyncSession, thread_id: UUID
) -> Optional[Thread]:
    """Eagerly load messages in a single query — avoids N+1."""
    result = await db.execute(
        select(Thread)
        .where(Thread.thread_id == thread_id)
        .options(
            selectinload(Thread.messages)
        )
    )
    return result.scalar_one_or_none()


async def get_or_create_thread(
    db: AsyncSession,
    user_id: UUID,
    article_id: Optional[str] = None,
) -> Thread:
    """
    Return existing thread for (user, article) pair or create a new one.
    article_id=None → global RAG thread (one per user).
    article_id set  → per-article scoped thread (one per user per article).
    """
    query = select(Thread).where(
        Thread.user_id == user_id,
        Thread.article_id == article_id,
    )
    result = await db.execute(query)
    thread = result.scalar_one_or_none()

    if not thread:
        thread = Thread(user_id=user_id, article_id=article_id)
        db.add(thread)
        await db.flush()
        await db.refresh(thread)

    return thread

async def get_threads_by_user(
    db: AsyncSession, user_id: UUID
) -> list[Thread]:
    """All threads for a user — global + all per-article threads."""
    result = await db.execute(
        select(Thread)
        .where(Thread.user_id == user_id)
        .order_by(Thread.updated_at.desc())
    )
    return list(result.scalars().all())

async def get_global_thread(
    db: AsyncSession, user_id: UUID
) -> Optional[Thread]:
    # Get Global Thread: One per user when QnA in homepage. Article_ID is none
    result = await db.execute(
        select(Thread).where(
            Thread.user_id == user_id,
            Thread.article_id.is_(None),
        )
    )
    return result.scalar_one_or_none()

async def delete_thread(db: AsyncSession, thread_id: UUID) -> bool:
    thread = await get_thread(db, thread_id)
    if not thread:
        return False
    await db.delete(thread)   # cascades to messages via ON DELETE CASCADE
    await db.flush()
    return True


async def delete_stale_threads(db: AsyncSession, days_old: int = 30) -> int:
    """
    Cron-friendly cleanup — remove threads untouched for N days.
    Returns count of deleted threads.
    """
    from datetime import datetime, timedelta
    from sqlalchemy import delete

    cutoff = datetime.utcnow() - timedelta(days=days_old)
    result = await db.execute(
        delete(Thread).where(Thread.updated_at < cutoff).returning(Thread.thread_id)
    )
    await db.flush()
    return len(result.fetchall())


# ══════════════════════════════════════════════════════════════════════════════
# MESSAGE
# ══════════════════════════════════════════════════════════════════════════════

async def append_message(
    db: AsyncSession,
    thread_id: UUID,
    data: MessageCreate,
) -> Message:
    """
    Append a single message to a thread.
    Automatically updates thread.updated_at via SQLAlchemy onupdate.
    """
    msg = Message(
        thread_id=thread_id,
        role=data.role,
        content=data.content,
        meta=data.meta.model_dump() if data.meta else None,
    )
    db.add(msg)
    await db.flush()
    await db.refresh(msg)
    return msg


async def get_message(db: AsyncSession, message_id: UUID) -> Optional[Message]:
    result = await db.execute(
        select(Message).where(Message.message_id == message_id)
    )
    return result.scalar_one_or_none()

async def get_thread_history(
    db: AsyncSession,
    thread_id: UUID,
    limit: Optional[int] = None,
) -> list[Message]:
    """
    Return messages ordered chronologically.
    limit: pass an int to fetch only the last N messages (sliding window context).
    """
    query = (
        select(Message)
        .where(Message.thread_id == thread_id)
        .order_by(Message.created_at.asc())
    )
    if limit:
        # Subquery to get last N rows, then sort asc for LangChain
        query = (
            select(Message)
            .where(Message.thread_id == thread_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
            .subquery()
        )
        query = (
            select(Message)
            .select_from(query)
            .order_by(query.c.created_at.asc())
        )

    result = await db.execute(query)
    return list(result.scalars().all())


async def to_langchain_messages(messages: list[Message]) -> list[dict]:
    """
    Convert DB messages to LangChain-compatible dict format.
    Pass the result directly to ChatGoogleGenerativeAI or any LangChain LLM.

    Usage:
        history = await get_thread_history(db, thread_id, limit=20)
        lc_messages = await to_langchain_messages(history)
    """
    role_map = {"human": "human", "ai": "ai", "tool": "tool"}
    return [
        {"role": role_map[msg.role], "content": msg.content}
        for msg in messages
    ]

async def delete_message(db: AsyncSession, message_id: UUID) -> bool:
    msg = await get_message(db, message_id)
    if not msg:
        return False
    await db.delete(msg)
    await db.flush()
    return True