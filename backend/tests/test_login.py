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

    data = response.json()
    assert response.status_code == 200
    assert data["status"] == "ok"
    assert data["name"] == get_test_data["users"]["admin"]
    assert isinstance(data["user_id"], int)
    assert data["is_admin"] is True
    assert "session_id" in response.cookies


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
    data = response.json()
    assert data["status"] == "ok"
    assert data["name"] == get_test_data["users"]["standard"]
    assert isinstance(data["user_id"], int)
    assert data["is_admin"] is False
    assert "session_id" in response.cookies


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


@pytest.mark.asyncio
async def test_unknown_user_login(get_test_data):

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url=get_test_data["base_url"],
    ) as client:
        response = await client.post(
            "/login",
            params={
                "name": "DefinitelyNotExistingUser",
                "password": "whatever",
            },
        )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout_returns_ok(get_test_data):
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url=get_test_data["base_url"],
    ) as client:
        response = await client.post("/logout")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_me_returns_logged_in_user(get_test_data):

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url=get_test_data["base_url"],
    ) as client:
        # Login first
        login = await client.post(
            "/login",
            params={
                "name": get_test_data["users"]["standard"],
                "password": get_test_data["pwd_usu"],
            },
        )

        assert login.status_code == 200

        # Ask backend who we are
        response = await client.get("/me")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == get_test_data["users"]["standard"]
        assert data["is_admin"] is False
