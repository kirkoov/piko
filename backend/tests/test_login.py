import pytest

from tests.helpers import assert_invalid_credentials, assert_ok


@pytest.mark.asyncio
async def test_admin_login_success(client, get_test_data):
    response = await client.post(
        f"{get_test_data['api_prefix']}/auth/login",
        params={
            "name": get_test_data["users"]["admin"],
            "password": get_test_data["pwd_admin"],
        },
    )

    data = assert_ok(response)

    assert data["status"] == "ok"
    assert data["name"] == get_test_data["users"]["admin"]
    assert isinstance(data["user_id"], int)
    assert data["is_admin"] is True


@pytest.mark.asyncio
async def test_admin_login_wrong_password(client, get_test_data):

    response = await client.post(
        f"{get_test_data['api_prefix']}/auth/login",
        params={
            "name": get_test_data["users"]["admin"],
            "password": "definitely_wrong_password",
        },
    )

    assert_invalid_credentials(response)


@pytest.mark.asyncio
async def test_standard_user_login_success(client, get_test_data):

    response = await client.post(
        f"{get_test_data['api_prefix']}/auth/login",
        params={
            "name": get_test_data["users"]["standard"],
            "password": get_test_data["pwd_usu"],
        },
    )

    data = assert_ok(response)

    assert data["status"] == "ok"
    assert data["name"] == get_test_data["users"]["standard"]
    assert isinstance(data["user_id"], int)
    assert data["is_admin"] is False


@pytest.mark.asyncio
async def test_standard_user_login_wrong_password(client, get_test_data):

    response = await client.post(
        f"{get_test_data['api_prefix']}/auth/login",
        params={
            "name": get_test_data["users"]["standard"],
            "password": "definitely_wrong_password",
        },
    )

    assert_invalid_credentials(response)


@pytest.mark.asyncio
async def test_unknown_user_login(client, get_test_data):

    response = await client.post(
        f"{get_test_data['api_prefix']}/auth/login",
        params={
            "name": "DefinitelyNotAnExistingUser",
            "password": "whatever",
        },
    )

    assert_invalid_credentials(response)


@pytest.mark.asyncio
async def test_logout_returns_ok(user_client, get_test_data):

    logout = await user_client.post(f"{get_test_data['api_prefix']}/auth/logout")

    assert logout.status_code == 200
    assert logout.json()["status"] == "ok"

    response = await user_client.get(f"{get_test_data['api_prefix']}/auth/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"


@pytest.mark.asyncio
async def test_me_returns_logged_in_admin(admin_client, get_test_data):

    response = await admin_client.get(f"{get_test_data['api_prefix']}/auth/me")

    data = assert_ok(response)

    assert data["name"] == get_test_data["users"]["admin"]
    assert data["is_admin"] is True


@pytest.mark.asyncio
async def test_me_returns_logged_in_user(user_client, get_test_data):

    response = await user_client.get(f"{get_test_data['api_prefix']}/auth/me")

    data = assert_ok(response)

    assert data["name"] == get_test_data["users"]["standard"]
    assert data["is_admin"] is False
