"""
database.py
Async SQLAlchemy engine using psycopg3 (compatible with Python 3.14)
"""

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger("spiritpulse.database")

_raw_url = os.getenv("DATABASE_URL", "")
DATABASE_URL = _raw_url.replace("postgresql://", "postgresql+psycopg://").replace("postgres://", "postgresql+psycopg://")
SCHEMA = os.getenv("DATABASE_SCHEMA", "spiritpulse")

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_connection() -> bool:
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False
