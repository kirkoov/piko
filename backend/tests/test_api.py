# DATABASE_URL=sqlite+aiosqlite:///./test.db uv run pytest


import uuid
from sys import maxsize

import pytest

from tests.helpers import assert_ok

TEST_BONUS_MINS = 239  # Provided the initial seed data never change & start @239 min


@pytest.mark.asyncio
async def test_create_user(admin_client, get_test_data):
    response = await admin_client.post(
        f"{get_test_data['api_prefix']}/users",
        params={
            "name": get_test_data["users"]["test_user_a"],
            "password": get_test_data["pwd_usu"],
        },
    )

    data = assert_ok(response)

    assert data["status"] == "created"
    assert data["name"] == get_test_data["users"]["test_user_a"]
    assert isinstance(data["id"], int)


@pytest.mark.asyncio
async def test_create_user_duplicate(admin_client, get_test_data):

    PARAMS = {
        "name": get_test_data["users"]["test_user_b"],
        "password": get_test_data["pwd_usu"],
    }

    await admin_client.post(
        f"{get_test_data['api_prefix']}/users",
        params=PARAMS,
    )

    response = await admin_client.post(
        f"{get_test_data['api_prefix']}/users",
        params=PARAMS,
    )

    data = response.json()
    assert data["status"] == "error"
    assert data["message"] == f"User '{PARAMS['name']}' already exists"


@pytest.mark.asyncio
async def test_delete_user(admin_client, get_test_data):

    test_user_name = "DeleteMe"

    create = await admin_client.post(
        f"{get_test_data['api_prefix']}/users",
        params={
            "name": test_user_name,
            "password": get_test_data["pwd_usu"],
        },
    )

    data = assert_ok(create)
    assert data["status"] == "created"
    assert data["name"] == test_user_name

    users = await admin_client.get(f"{get_test_data['api_prefix']}/users")
    user_id = next(u["id"] for u in users.json() if u["name"] == test_user_name)

    response = await admin_client.delete(
        f"{get_test_data['api_prefix']}/users/{user_id}"
    )

    data = assert_ok(response)
    assert data["status"] == "deleted"
    assert data["id"] == user_id

    users = await admin_client.get(f"{get_test_data['api_prefix']}/users")
    names = {u["name"] for u in users.json()}

    assert test_user_name not in names


@pytest.mark.asyncio
async def test_delete_user_not_found(admin_client, get_test_data):

    response = await admin_client.delete(
        f"{get_test_data['api_prefix']}/users/{maxsize}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


@pytest.mark.asyncio
async def test_get_users(admin_client, get_test_data):
    response = await admin_client.get(f"{get_test_data['api_prefix']}/users")

    data = assert_ok(response)

    assert isinstance(data, list)
    expected_users = set(get_test_data["users"].values())
    returned_users = {u["name"] for u in data}
    assert expected_users.issubset(returned_users)


@pytest.mark.asyncio
async def test_create_shift_success(user_client, get_test_data):

    response = await user_client.post(
        f"{get_test_data['api_prefix']}/shifts",
        json=get_test_data["shift_params"],
    )

    data = assert_ok(response)

    assert data["status"] == "created"
    assert isinstance(data["shift_id"], int)


@pytest.mark.asyncio
async def test_update_shift(user_client, get_test_data):
    shift = get_test_data["shift_params"].copy()
    shift["date"] = "2100-01-02"

    create = await user_client.post(
        f"{get_test_data['api_prefix']}/shifts",
        json=shift,
    )

    data = assert_ok(create)
    shift_id = data["shift_id"]

    update_data = {
        "planned_start": "08:00",
        "planned_end": "16:00",
        "actual_start": "08:00",
        "actual_end": "17:00",
        "latest_child_name": "Sara",
        "latest_child_time": "16:30",
        "note": "Matti leaves later",
    }

    response = await user_client.put(
        f"{get_test_data['api_prefix']}/shifts/{shift_id}",
        json=update_data,
    )

    data = assert_ok(response)

    assert data["status"] == "updated"
    assert data["shift_id"] == shift_id

    response = await user_client.get(f"{get_test_data['api_prefix']}/shifts")

    shifts = assert_ok(response)

    updated = next(s for s in shifts if s["id"] == shift_id)

    assert updated["actual"] == "08:00-17:00"
    assert updated["note"] == "Matti leaves later"
    assert updated["latest_child_name"] == "Sara"


@pytest.mark.asyncio
async def test_create_shift_duplicate(user_client, get_test_data):
    assert_ok(
        await user_client.post(
            f"{get_test_data['api_prefix']}/shifts", json=get_test_data["shift_params"]
        )
    )

    response = await user_client.post(
        f"{get_test_data['api_prefix']}/shifts", json=get_test_data["shift_params"]
    )

    data = response.json()
    assert data["status"] == "error"
    assert "already" in data["message"].lower()


@pytest.mark.asyncio
async def test_create_shift_bad_date(user_client, get_test_data):

    bad = get_test_data["shift_params"].copy()
    bad["date"] = "banana"

    response = await user_client.post(f"{get_test_data['api_prefix']}/shifts", json=bad)

    assert response.status_code != 200


@pytest.mark.asyncio
async def test_create_shift_end_before_start(user_client, get_test_data):

    bad = get_test_data["shift_params"].copy()
    bad["actual_start"] = "16:00"
    bad["actual_end"] = "08:00"

    response = await user_client.post(f"{get_test_data['api_prefix']}/shifts", json=bad)

    assert response.status_code == 400
    assert response.json()["detail"] == "Actual shift end must be after start"


@pytest.mark.asyncio
async def test_get_shifts(user_client, get_test_data):

    assert_ok(
        await user_client.post(
            f"{get_test_data['api_prefix']}/shifts",
            json=get_test_data["shift_params"],
        )
    )

    response = await user_client.get(f"{get_test_data['api_prefix']}/shifts")

    data = assert_ok(response)

    assert len(data) > 0

    shift = data[0]

    assert "id" in shift
    assert "planned" in shift
    assert "actual" in shift
    assert "date" in shift


@pytest.mark.asyncio
async def test_update_shift_not_found(user_client, get_test_data):

    response = await user_client.put(
        f"{get_test_data['api_prefix']}/shifts/{maxsize}",
        json={
            "planned_start": "08:00",
            "planned_end": "16:00",
            "actual_start": "08:00",
            "actual_end": "16:00",
            "latest_child_name": "Test",
            "latest_child_time": "15:00",
            "note": "This update is supposed to be never saved!",
        },
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_shifts_empty_user(empty_user_client, get_test_data):

    response = await empty_user_client.get(f"{get_test_data['api_prefix']}/shifts")

    assert assert_ok(response) == []


@pytest.mark.asyncio
async def test_delete_shift(user_client, get_test_data):

    shift = get_test_data["shift_params"].copy()
    shift["date"] = "2099-12-31"

    create = await user_client.post(f"{get_test_data['api_prefix']}/shifts", json=shift)

    shift_id = assert_ok(create)["shift_id"]

    response = await user_client.delete(
        f"{get_test_data['api_prefix']}/shifts/{shift_id}"
    )

    assert assert_ok(response)["status"] == "deleted"


@pytest.mark.asyncio
async def test_delete_shift_not_found(user_client, get_test_data):

    response = await user_client.delete(
        f"{get_test_data['api_prefix']}/shifts/{maxsize}"
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_balance(user_client, get_test_data):

    shift_ids = []

    shift_1 = get_test_data["shift_params"].copy()
    shift_1["date"] = "2120-01-01"

    response = await user_client.post(
        f"{get_test_data['api_prefix']}/shifts",
        json=shift_1,
    )

    data = assert_ok(response)
    assert data["status"] == "created"
    assert isinstance(data["shift_id"], int)
    shift_ids.append(data["shift_id"])

    shift_2 = get_test_data["shift_params"].copy()
    shift_2["date"] = "2120-01-03"

    data = assert_ok(
        await user_client.post(
            f"{get_test_data['api_prefix']}/shifts",
            json=shift_2,
        )
    )
    shift_ids.append(data["shift_id"])

    response = await user_client.get(f"{get_test_data['api_prefix']}/balance")

    assert "balance_minutes" in assert_ok(response)

    for shift_id in shift_ids:
        response = await user_client.delete(
            f"{get_test_data['api_prefix']}/shifts/{shift_id}"
        )
        assert assert_ok(response)["status"] == "deleted"


@pytest.mark.asyncio
async def test_get_balance_empty_user(empty_user_client, get_test_data):

    response = await empty_user_client.get(f"{get_test_data['api_prefix']}/balance")

    assert assert_ok(response)["balance_minutes"] == 0


@pytest.mark.asyncio
async def test_get_balance_calculated(user_client, get_test_data):

    response = await user_client.get(f"{get_test_data['api_prefix']}/balance")

    data = assert_ok(response)

    assert "balance_minutes" in data
    assert data["user_id"] == get_test_data["shift_params"]["user_id"]
    assert data["balance_minutes"] == TEST_BONUS_MINS


@pytest.mark.asyncio
async def test_get_current_period(user_client, get_test_data):

    response = await user_client.get(f"{get_test_data['api_prefix']}/periods/current")

    data = assert_ok(response)

    assert "period_start" in data
    assert "period_end" in data
    assert "shifts" in data
    assert isinstance(data["shifts"], list)
    assert data["period_start"] <= data["period_end"]


@pytest.mark.asyncio
async def test_get_current_period_empty_user(empty_user_client, get_test_data):

    response = await empty_user_client.get(
        f"{get_test_data['api_prefix']}/periods/current"
    )
    assert assert_ok(response)["shifts"] == []


@pytest.mark.asyncio
async def test_get_periods(user_client, get_test_data):

    response = await user_client.get(f"{get_test_data['api_prefix']}/periods")

    periods = assert_ok(response)

    assert isinstance(periods, list)
    assert len(periods) >= 1

    period = periods[0]

    assert "period_start" in period
    assert "period_end" in period
    assert "balance_minutes" in period
    assert "shift_count" in period
    assert "shifts" in period

    assert isinstance(period["shifts"], list)


@pytest.mark.asyncio
async def test_get_periods_empty_user(empty_user_client, get_test_data):

    response = await empty_user_client.get(f"{get_test_data['api_prefix']}/periods")

    assert assert_ok(response) == []


@pytest.mark.asyncio
# @pytest.mark.skip(reason="Earlier tests may have change pwd and spoilt the run")
async def test_change_user_password(admin_client, client, get_test_data):

    temp_name = f"TempUser-{uuid.uuid4().hex[:8]}"

    response = await admin_client.post(
        f"{get_test_data['api_prefix']}/users",
        params={
            "name": temp_name,
            "password": "initial_password",
        },
    )

    data = assert_ok(response)
    assert data["status"] == "created"
    user_id = data["id"]

    response = await admin_client.put(
        f"{get_test_data['api_prefix']}/users/{user_id}/password",
        params={
            "password": "new_password",
        },
    )

    data = assert_ok(response)

    assert data["status"] == "password changed"
    assert data["id"] == user_id

    response = await client.post(
        f"{get_test_data['api_prefix']}/auth/login",
        params={
            "name": temp_name,
            "password": "new_password",
        },
    )

    data = assert_ok(response)
    assert "access_token" in data
