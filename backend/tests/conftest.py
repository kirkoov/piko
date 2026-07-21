import os
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.config import API_PREFIX
from app.database import engine
from app.main import app
from app.models import Base
from init_with_data import main as seed_data

TEST_DATA: dict[str, Any] = {
    "base_url": "http://test",
    "api_prefix": API_PREFIX,
    "users": {
        "admin": "kk",
        "standard": "Lora",
        "empty": "Masha",
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


def make_client():
    return AsyncClient(
        transport=ASGITransport(app=app),
        base_url=TEST_DATA["base_url"],
    )


async def login(client, username, password):
    response = await client.post(
        f"{TEST_DATA['api_prefix']}/auth/login",
        params={
            "name": username,
            "password": password,
        },
    )

    assert response.status_code == 200
    token = response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return response.json()


async def login_as(client, role):
    passwords = {
        "admin": TEST_DATA["pwd_admin"],
        "standard": TEST_DATA["pwd_usu"],
        "empty": TEST_DATA["pwd_usu"],
    }

    usernames = {
        "admin": TEST_DATA["users"]["admin"],
        "standard": TEST_DATA["users"]["standard"],
        "empty": TEST_DATA["users"]["empty"],
    }

    try:
        return await login(
            client,
            usernames[role],
            passwords[role],
        )
    except KeyError:
        raise ValueError(f"Unknown role: {role}")


@pytest.fixture
def get_test_data():
    return TEST_DATA


@pytest.fixture
def shift_params(get_test_data):
    params = get_test_data["shift_params"].copy()
    params.pop("user_id", None)
    return params


@pytest_asyncio.fixture
async def client():
    async with make_client() as client:
        yield client


@pytest_asyncio.fixture
async def empty_user_client():
    async with make_client() as client:
        await login_as(client, "empty")
        yield client


@pytest_asyncio.fixture
async def user_client():
    async with make_client() as client:
        await login_as(client, "standard")
        yield client


@pytest_asyncio.fixture
async def admin_client():
    async with make_client() as client:
        await login_as(client, "admin")
        yield client


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():

    if os.path.exists("test.db"):
        os.remove("test.db")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await seed_data()

    yield

    await engine.dispose()
