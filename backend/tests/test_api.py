# DATABASE_URL=sqlite+aiosqlite:///./test.db uv run pytest

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app

BASE_URL = "http://test"
TEST_SHIFT_PARAMS: dict[str, str | int] = {
    "user_id": 1,
    "date": "2026-06-14",
    "planned_start": "08:00",
    "planned_end": "16:00",
    "actual_start": "08:00",
    "actual_end": "16:00",
    "latest_child_name": "Matti",
    "latest_child_time": "15:30",
    "note": "",
}


@pytest.mark.asyncio
async def test_create_user():

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url=BASE_URL,
    ) as client:
        response = await client.post(
            "/users",
            params={"name": "Alice"},
        )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "created"
    assert data["name"] == "Alice"


@pytest.mark.asyncio
async def test_create_shift_success():

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url=BASE_URL,
    ) as client:
        response = await client.post(
            "/shifts",
            params=TEST_SHIFT_PARAMS,
        )

    data = response.json()
    assert data["status"] == "created"
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_shift_duplicate():

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url=BASE_URL,
    ) as client:
        await client.post("/shifts", params=TEST_SHIFT_PARAMS)

        response = await client.post(
            "/shifts",
            params=TEST_SHIFT_PARAMS,
        )

    data = response.json()
    assert data["status"] == "error"


@pytest.mark.asyncio
async def test_create_shift_bad_date():
    BAD_DATE = TEST_SHIFT_PARAMS.copy()
    BAD_DATE["date"] = "banana"

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url=BASE_URL,
    ) as client:
        response = await client.post(
            "/shifts",
            params=BAD_DATE,
        )

    assert response.status_code != 200


@pytest.mark.asyncio
async def test_create_shift_end_before_start():

    BAD_END = TEST_SHIFT_PARAMS.copy()
    BAD_END["actual_start"] = "16:00"
    BAD_END["actual_end"] = "08:00"

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url=BASE_URL,
    ) as client:
        response = await client.post(
            "/shifts",
            params=BAD_END,
        )
    
    print(response.status_code)
    print(response.json())

    assert response.status_code == 400
