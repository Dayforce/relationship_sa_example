from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

import config

engine = create_async_engine(
    f"postgresql+asyncpg://{config.DB_USER}:{config.DB_PASS}@{config.DB_HOST}/{config.DB_NAME}",
)


async def create_db_session():
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    return async_session
