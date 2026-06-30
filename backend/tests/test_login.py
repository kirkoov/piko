import pytest


def assert_invalid_credentials(response):
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


@pytest.mark.asyncio
async def test_admin_login_success(client, get_test_data):
    response = await client.post(
        "/login",
        params={
            "name": get_test_data["users"]["admin"],
            "password": get_test_data["pwd_admin"],
        },
    )
    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["name"] == get_test_data["users"]["admin"]
    assert isinstance(data["user_id"], int)
    assert data["is_admin"] is True


@pytest.mark.asyncio
async def test_admin_login_wrong_password(client, get_test_data):

    response = await client.post(
        "/login",
        params={
            "name": get_test_data["users"]["admin"],
            "password": "definitely_wrong_password",
        },
    )

    assert_invalid_credentials(response)


@pytest.mark.asyncio
async def test_standard_user_login_success(client, get_test_data):

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


@pytest.mark.asyncio
async def test_standard_user_login_wrong_password(client, get_test_data):

    response = await client.post(
        "/login",
        params={
            "name": get_test_data["users"]["standard"],
            "password": "definitely_wrong_password",
        },
    )

    assert_invalid_credentials(response)


@pytest.mark.asyncio
async def test_unknown_user_login(client):

    response = await client.post(
        "/login",
        params={
            "name": "DefinitelyNotAnExistingUser",
            "password": "whatever",
        },
    )

    assert_invalid_credentials(response)


@pytest.mark.asyncio
async def test_logout_returns_ok(user_client):

    logout = await user_client.post("/logout")

    assert logout.status_code == 200
    assert logout.json()["status"] == "ok"

    response = await user_client.get("/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"


@pytest.mark.asyncio
async def test_me_returns_logged_in_admin(admin_client, get_test_data):

    response = await admin_client.get("/me")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == get_test_data["users"]["admin"]
    assert data["is_admin"] is True


@pytest.mark.asyncio
async def test_me_returns_logged_in_user(user_client, get_test_data):

    response = await user_client.get("/me")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == get_test_data["users"]["standard"]
    assert data["is_admin"] is False
