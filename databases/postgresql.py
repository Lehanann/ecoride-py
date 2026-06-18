from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.core.settings import settings
from collections.abc import AsyncGenerator

#Creating async engine
engine = create_async_engine(
    settings.dsn_async,
    echo=True,
)

Base = declarative_base(metadata=MetaData(schema=settings.PG_SCHEMA))

# Fabric async session
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)

async def get_session()->AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session