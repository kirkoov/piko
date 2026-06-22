import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app

BASE_URL = "http://test"


@pytest.mark.asyncio
async def test_login_success():

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url=BASE_URL,
    ) as client:
        response = await client.post(
            "/login",
            params={
                "name": "kk",
                "password": "test123",
            },
        )

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_login_wrong_password():

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url=BASE_URL,
    ) as client:
        response = await client.post(
            "/login",
            params={
                "name": "kk",
                "password": "wrong",
            },
        )

    assert response.status_code == 401
