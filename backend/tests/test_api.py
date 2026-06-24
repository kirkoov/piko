# DATABASE_URL=sqlite+aiosqlite:///./test.db uv run pytest

from sys import maxsize

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_create_user(get_test_data):
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url=get_test_data["base_url"],
    ) as client:
        response = await client.post(
            "/users",
            params={
                "name": get_test_data["users"]["test_user_a"],
                "password": get_test_data["pwd_usu"],
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "created"
    assert data["name"] == get_test_data["users"]["test_user_a"]


@pytest.mark.asyncio
async def test_create_user_duplicate(get_test_data):
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url=get_test_data["base_url"],
    ) as client:
        await client.post(
            "/users",
            params={
                "name": get_test_data["users"]["test_user_b"],
                "password": get_test_data["pwd_usu"],
            },
        )

        response = await client.post(
            "/users",
            params={
                "name": get_test_data["users"]["test_user_b"],
                "password": get_test_data["pwd_usu"],
            },
        )

    data = response.json()
    assert data["status"] == "error"


@pytest.mark.asyncio
async def test_get_users(get_test_data):
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url=get_test_data["base_url"],
    ) as client:
        response = await client.get("/users")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

    expected_users = set(get_test_data["users"].values())
    returned_users = {u["name"] for u in data}
    assert expected_users.issubset(returned_users)


@pytest.mark.asyncio
async def test_create_shift_success(get_test_data):
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url=get_test_data["base_url"],
    ) as client:
        response = await client.post(
            "/shifts",
            params=get_test_data["shift_params"],
        )

    data = response.json()
    assert data["status"] == "created"
    assert data["shift_id"] >= 1
    assert response.status_code == 200
    assert data["status"] == "created"
    assert isinstance(data["shift_id"], int)


# @pytest.mark.asyncio
# async def test_update_shift():

#     transport = ASGITransport(app=app)

#     UPDATER = TEST_SHIFT_PARAMS.copy()
#     del UPDATER["user_id"]
#     del UPDATER["date"]
#     UPDATER["actual_end"] = "17:00"
#     UPDATER["latest_child_name"] = "Sara"
#     UPDATER["latest_child_time"] = "16:30"
#     UPDATER["note"] = "Matti leaves later"

#     async with AsyncClient(
#         transport=transport,
#         base_url=get_test_data["base_url"],
#     ) as client:
#         response = await client.put(
#             "/shifts/1",
#             json=UPDATER,
#         )

#         assert response.status_code == 200
#         data = response.json()
#         assert data["status"] == "updated"
#         assert data["shift_id"] == 1

#         response = await client.get(
#             "/shifts",
#             params={"user_id": 1},
#         )

#         shifts = response.json()

#     assert shifts[0]["actual"] == "08:00-17:00"
#     assert shifts[0]["note"] == "Matti leaves later"


@pytest.mark.asyncio
async def test_create_shift_duplicate(get_test_data):
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url=get_test_data["base_url"],
    ) as client:
        await client.post("/shifts", params=get_test_data["shift_params"])

        response = await client.post(
            "/shifts",
            params=get_test_data["shift_params"],
        )

    data = response.json()
    assert data["status"] == "error"
    assert "already" in data["message"].lower()


@pytest.mark.asyncio
async def test_create_shift_bad_date(get_test_data):
    BAD_DATE = get_test_data["shift_params"].copy()
    BAD_DATE["date"] = "banana"
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url=get_test_data["base_url"],
    ) as client:
        response = await client.post(
            "/shifts",
            params=BAD_DATE,
        )

    assert response.status_code != 200


@pytest.mark.asyncio
async def test_create_shift_end_before_start(get_test_data):
    BAD_END = get_test_data["shift_params"].copy()
    BAD_END["actual_start"] = "16:00"
    BAD_END["actual_end"] = "08:00"
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url=get_test_data["base_url"],
    ) as client:
        response = await client.post(
            "/shifts",
            params=BAD_END,
        )

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Actual shift end must be after start"


# @pytest.mark.asyncio
# async def test_get_balance():

#     transport = ASGITransport(app=app)

#     async with AsyncClient(
#         transport=transport,
#         base_url=get_test_data["base_url"],
#     ) as client:
#         response = await client.get(
#             "/balance",
#             params={"user_id": 1},
#         )

#     assert response.status_code == 200
#     data = response.json()
#     assert "balance_minutes" in data
#     # Planned 08-16 (480 min)
#     # Actual 08-17 (540 min)
#     # Difference = +60
#     assert data["balance_minutes"] == 60


# @pytest.mark.asyncio
# async def test_get_balance_unknown_user():

#     transport = ASGITransport(app=app)

#     async with AsyncClient(
#         transport=transport,
#         base_url=get_test_data["base_url"],
#     ) as client:
#         response = await client.get(
#             "/balance",
#             params={"user_id": 999},
#         )

#     assert response.status_code == 404
#     data = response.json()
#     assert data["detail"] == "User not found"


# @pytest.mark.asyncio
# async def test_get_balance_empty_user():

#     transport = ASGITransport(app=app)

#     async with AsyncClient(
#         transport=transport,
#         base_url=get_test_data["base_url"],
#     ) as client:
#         await client.post(
#             "/users",
#             params={"name": "Bob"},
#         )

#         response = await client.get(
#             "/balance",
#             params={"user_id": 2},
#         )

#     data = response.json()

#     assert response.status_code == 200
#     assert data["balance_minutes"] == 0


# @pytest.mark.asyncio
# async def test_get_balance_calculated():

#     transport = ASGITransport(app=app)

#     async with AsyncClient(
#         transport=transport,
#         base_url=get_test_data["base_url"],
#     ) as client:
#         response = await client.get(
#             "/balance",
#             params={"user_id": 1},
#         )

#     data = response.json()

#     assert response.status_code == 200
#     assert "balance_minutes" in data
#     assert data["user_id"] == 1


@pytest.mark.asyncio
async def test_get_shifts(get_test_data):
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url=get_test_data["base_url"],
    ) as client:
        response = await client.get(
            "/shifts",
            params={"user_id": get_test_data["shift_params"]["user_id"]},
        )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert isinstance(data[0], dict)
    assert len(data) >= 1

    shift = next(s for s in data if s["date"] == get_test_data["shift_params"]["date"])
    assert "id" in shift
    assert "date" in shift
    assert "actual" in shift
    assert "planned" in shift


@pytest.mark.asyncio
async def test_delete_shift(get_test_data):
    new_shift = get_test_data["shift_params"].copy()
    new_shift["date"] = "2099-12-31"
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url=get_test_data["base_url"],
    ) as client:
        create = await client.post("/shifts", params=new_shift)

        shift_id = create.json()["shift_id"]

        response = await client.delete(f"/shifts/{shift_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "deleted"


@pytest.mark.asyncio
async def test_update_shift_not_found(get_test_data):

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url=get_test_data["base_url"],
    ) as client:
        response = await client.put(
            f"/shifts/{maxsize}",
            json={
                "planned_start": "08:00",
                "planned_end": "16:00",
                "actual_start": "08:00",
                "actual_end": "16:00",
                "latest_child_name": "Test",
                "latest_child_time": "15:00",
                "note": "This code is supposed to be never reached!",
            },
        )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_shift_not_found(get_test_data):

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url=get_test_data["base_url"],
    ) as client:
        response = await client.delete(f"/shifts/{maxsize}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_shifts_empty_user(get_test_data):

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url=get_test_data["base_url"],
    ) as client:
        response = await client.get(
            "/shifts",
            params={"user_id": maxsize},
        )

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_current_period(get_test_data):

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url=get_test_data["base_url"],
    ) as client:
        response = await client.get(
            "/current-period",
            params={"user_id": get_test_data["shift_params"]["user_id"]},
        )

    assert response.status_code == 200

    data = response.json()

    assert "period_start" in data
    assert "period_end" in data
    assert "shifts" in data
    assert isinstance(data["shifts"], list)
    assert data["period_start"] <= data["period_end"]
