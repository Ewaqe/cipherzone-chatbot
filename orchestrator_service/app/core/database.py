from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager

from app.core.logging import logger
from app.core.config import PG_LOGIN, PG_PASSWORD, PG_DB
from shared.models import Base


DATABASE_URL = f"postgresql+asyncpg://{PG_LOGIN}:{PG_PASSWORD}@postgres:5432/{PG_DB}"


engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


@asynccontextmanager
async def use_session():
    gen = get_session()
    session = await gen.__anext__()
    try:
        yield session
    finally:
        await gen.aclose()

