import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_admin_login_success(get_test_data):

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url=get_test_data["base_url"],
    ) as client:
        response = await client.post(
            "/login",
            params={
                "name": get_test_data["users"]["admin"],
                "password": get_test_data["pwd_admin"],
            },
        )

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_admin_login_wrong_password(get_test_data):

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url=get_test_data["base_url"],
    ) as client:
        response = await client.post(
            "/login",
            params={
                "name": get_test_data["users"]["admin"],
                "password": "wrongAhem",
            },
        )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_standard_user_login_success(get_test_data):

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url=get_test_data["base_url"],
    ) as client:
        response = await client.post(
            "/login",
            params={
                "name": get_test_data["users"]["standard"],
                "password": get_test_data["pwd_usu"],
            },
        )

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_standard_user_login_wrong_password(get_test_data):

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url=get_test_data["base_url"],
    ) as client:
        response = await client.post(
            "/login",
            params={
                "name": get_test_data["users"]["standard"],
                "password": "wrongAhem",
            },
        )

    assert response.status_code == 401
