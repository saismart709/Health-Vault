from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

import os

# Use /tmp for SQLite on Vercel to avoid read-only filesystem errors
if os.environ.get("VERCEL"):
    DATABASE_URL = "sqlite+aiosqlite:////tmp/health_vault.db"
else:
    DATABASE_URL = "sqlite+aiosqlite:///./health_vault.db"

engine = create_async_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with SessionLocal() as session:
        yield session
