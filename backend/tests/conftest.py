import os

import pytest_asyncio

from app.database import engine
from app.models import Base
from init_with_data import main as seed_data


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():

    if os.path.exists("test.db"):
        os.remove("test.db")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await seed_data()

    yield
