import os

from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./piko.db",
)

engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("SQL_ECHO") == "1",
)

print("DATABASE =", DATABASE_URL)
print("ENGINE DB =", engine.url)

SessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)
