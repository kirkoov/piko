# DATABASE_URL=sqlite+aiosqlite:///./test.db uv run pytest

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_create_user():

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/users",
            params={"name": "Alice"},
        )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "created"
    assert data["name"] == "Alice"


def test_create_shift_success(): ...


def test_create_shift_duplicate(): ...


def test_create_shift_bad_date(): ...


def test_create_shift_end_before_start(): ...
