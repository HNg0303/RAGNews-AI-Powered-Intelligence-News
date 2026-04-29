from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from .config import DATABASE_URL


# ── Engine ────────────────────────────────────────────────────────────────────
# NullPool is recommended for async + serverless/short-lived connections.
# For a long-running server, swap to AsyncAdaptedQueuePool with pool_size=10.
engine = create_async_engine(
    DATABASE_URL,
    poolclass=NullPool,
    echo=False,         # set True to log all SQL — useful during dev
)

# ── Session factory ───────────────────────────────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # keep objects usable after commit without re-query
)

# ── Declarative base ──────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    pass

# ── Dependency / context manager ─────────────────────────────────────────────
async def get_db() -> AsyncSession:
    """
    FastAPI dependency — yields an async session and guarantees cleanup.

    Usage:
        @app.get("/")
        async def route(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Create all tables on startup (dev/test only).
    For production, use Alembic migrations instead.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db() -> None:
    """Drop all tables — useful for test teardown."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)