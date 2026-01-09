from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool
from contextlib import asynccontextmanager
from config import settings

params = {"poolclass": NullPool} if settings.mode == "TEST" else {}

engine = create_async_engine(settings.db.url, echo=False, **params)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@asynccontextmanager
async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

class Base(DeclarativeBase):
    pass