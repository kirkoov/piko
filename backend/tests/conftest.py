import os

import pytest
import pytest_asyncio

from app.database import engine
from app.models import Base
from init_with_data import main as seed_data


@pytest.fixture
def get_test_data():
    return {
        "base_url": "http://test",
        "users": {
            "admin": "kk",
            "standard": "Lora",
            "potential": "Masha",
            "test_user_a": "A",
            "test_user_b": "B",
        },
        "pwd_usu": "change_me",
        "pwd_admin": "test123",
        "shift_params": {
            "user_id": 2,
            "date": "2026-06-14",
            "planned_start": "08:00",
            "planned_end": "16:00",
            "actual_start": "08:00",
            "actual_end": "16:00",
            "latest_child_name": "Matti",
            "latest_child_time": "15:30",
            "note": "Notes come here",
        },
    }


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():

    if os.path.exists("test.db"):
        os.remove("test.db")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await seed_data()

    yield
