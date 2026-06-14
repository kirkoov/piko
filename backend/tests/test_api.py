# DATABASE_URL=sqlite+aiosqlite:///./test.db uv run pytest
# SQL_ECHO=1 ./check.sh
# ./check.sh

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
async def test_update_shift():

    transport = ASGITransport(app=app)

    UPDATER = TEST_SHIFT_PARAMS.copy()
    del UPDATER["user_id"]
    del UPDATER["date"]
    UPDATER["actual_end"] = "17:00"
    UPDATER["latest_child_name"] = "Sara"
    UPDATER["latest_child_time"] = "16:30"
    UPDATER["note"] = "Matti leaves later"

    async with AsyncClient(
        transport=transport,
        base_url=BASE_URL,
    ) as client:
        response = await client.put(
            "/shifts/1",
            json=UPDATER,
        )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "updated"
    assert data["shift_id"] == 1


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


@pytest.mark.asyncio
async def test_get_balance():

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url=BASE_URL,
    ) as client:
        response = await client.get(
            "/balance",
            params={"user_id": 1},
        )

    assert response.status_code == 200
    data = response.json()
    assert "balance_minutes" in data
    assert data["balance_minutes"] == 60


@pytest.mark.asyncio
async def test_get_shifts():

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url=BASE_URL,
    ) as client:
        response = await client.get(
            "/shifts",
            params={"user_id": 1},
        )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert isinstance(data[0], dict)
    assert len(data) >= 1
    assert any(s["date"] == "2026-06-14" for s in data)
    assert data[0]["actual"] == "08:00-17:00"
    assert data[0]["note"] == "Matti leaves later"


@pytest.mark.asyncio
async def test_delete_shift():

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url=BASE_URL,
    ) as client:
        response = await client.delete("/shifts/1")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "deleted"
