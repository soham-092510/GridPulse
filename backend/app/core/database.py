import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from app.core.config import settings

# Async Engine for FastAPI async handlers
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Sync Engine for batch seeding, data manipulation, and pandas support
sync_engine = create_engine(
    settings.SYNC_DATABASE_URL,
    echo=False,
    future=True
)

SessionLocalSync = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

def get_sync_db():
    db = SessionLocalSync()
    try:
        yield db
    finally:
        db.close()

async def init_db():
    """Initializes the database schema."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
