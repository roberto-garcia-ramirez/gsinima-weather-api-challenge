from __future__ import annotations
import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import get_settings

settings = get_settings()

# Ensure the database URL is absolute when using SQLite
db_url = settings.DATABASE_URL
if db_url.startswith("sqlite") and not db_url.startswith("sqlite:////"):
    # If it is sqlite:///./weather.db, convert it to an absolute path at the backend root
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(base_dir, "weather.db")
    db_url = f"sqlite+aiosqlite:///{db_path}"

engine = create_async_engine(
    db_url,
    future=True,
    echo=False,
)

AsyncSessionFactory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionFactory() as session:
        yield session