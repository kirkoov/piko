# # DATABASE_URL=sqlite+aiosqlite:///./test.db uv run pytest
# # SQL_ECHO=1 ./check.sh
# # ./check.sh

# import pytest
# from httpx import ASGITransport, AsyncClient

# from app.main import app

# PWD = "secret123"
# USERS = ["TestUser_A", "TestUser_B"]

# BASE_URL = "http://test"
# TEST_SHIFT_PARAMS: dict[str, str | int] = {
#     "user_id": 1,
#     "date": "2026-06-14",
#     "planned_start": "08:00",
#     "planned_end": "16:00",
#     "actual_start": "08:00",
#     "actual_end": "16:00",
#     "latest_child_name": "Matti",
#     "latest_child_time": "15:30",
#     "note": "Notes come here",
# }


# @pytest.mark.asyncio
# async def test_create_user():
#     transport = ASGITransport(app=app)
#     async with AsyncClient(
#         transport=transport,
#         base_url=BASE_URL,
#     ) as client:
#         response = await client.post(
#             "/users",
#             params={
#                 "name": USERS[0],
#                 "password": PWD,
#             },
#         )

#     assert response.status_code == 200
#     data = response.json()
#     assert data["status"] == "created"
#     assert data["name"] == USERS[0]


# @pytest.mark.asyncio
# async def test_create_user_duplicate():
#     transport = ASGITransport(app=app)
#     async with AsyncClient(
#         transport=transport,
#         base_url=BASE_URL,
#     ) as client:
#         await client.post(
#             "/users",
#             params={
#                 "name": USERS[1],
#                 "password": PWD,
#             },
#         )

#         response = await client.post(
#             "/users",
#             params={
#                 "name": USERS[1],
#                 "password": PWD,
#             },
#         )

#     data = response.json()
#     assert data["status"] == "error"


# @pytest.mark.asyncio
# async def test_get_users():
#     transport = ASGITransport(app=app)
#     async with AsyncClient(
#         transport=transport,
#         base_url=BASE_URL,
#     ) as client:
#         response = await client.get("/users")

#     assert response.status_code == 200
#     data = response.json()
#     assert isinstance(data, list)
#     assert len(data) >= 1
#     assert any(u["name"] == USERS[0] for u in data)
#     assert any(u["name"] == USERS[1] for u in data)


# @pytest.mark.asyncio
# async def test_create_shift_success():
#     transport = ASGITransport(app=app)
#     async with AsyncClient(
#         transport=transport,
#         base_url=BASE_URL,
#     ) as client:
#         response = await client.post(
#             "/shifts",
#             params=TEST_SHIFT_PARAMS,
#         )

#     data = response.json()
#     assert data["status"] == "created"
#     assert response.status_code == 200


# # @pytest.mark.asyncio
# # async def test_update_shift():

# #     transport = ASGITransport(app=app)

# #     UPDATER = TEST_SHIFT_PARAMS.copy()
# #     del UPDATER["user_id"]
# #     del UPDATER["date"]
# #     UPDATER["actual_end"] = "17:00"
# #     UPDATER["latest_child_name"] = "Sara"
# #     UPDATER["latest_child_time"] = "16:30"
# #     UPDATER["note"] = "Matti leaves later"

# #     async with AsyncClient(
# #         transport=transport,
# #         base_url=BASE_URL,
# #     ) as client:
# #         response = await client.put(
# #             "/shifts/1",
# #             json=UPDATER,
# #         )

# #         assert response.status_code == 200
# #         data = response.json()
# #         assert data["status"] == "updated"
# #         assert data["shift_id"] == 1

# #         response = await client.get(
# #             "/shifts",
# #             params={"user_id": 1},
# #         )

# #         shifts = response.json()

# #     assert shifts[0]["actual"] == "08:00-17:00"
# #     assert shifts[0]["note"] == "Matti leaves later"


# @pytest.mark.asyncio
# async def test_create_shift_duplicate():
#     transport = ASGITransport(app=app)
#     async with AsyncClient(
#         transport=transport,
#         base_url=BASE_URL,
#     ) as client:
#         await client.post("/shifts", params=TEST_SHIFT_PARAMS)

#         response = await client.post(
#             "/shifts",
#             params=TEST_SHIFT_PARAMS,
#         )

#     data = response.json()
#     assert data["status"] == "error"
#     assert "already" in data["message"].lower()


# @pytest.mark.asyncio
# async def test_create_shift_bad_date():
#     BAD_DATE = TEST_SHIFT_PARAMS.copy()
#     BAD_DATE["date"] = "banana"
#     transport = ASGITransport(app=app)

#     async with AsyncClient(
#         transport=transport,
#         base_url=BASE_URL,
#     ) as client:
#         response = await client.post(
#             "/shifts",
#             params=BAD_DATE,
#         )

#     assert response.status_code != 200


# @pytest.mark.asyncio
# async def test_create_shift_end_before_start():

#     BAD_END = TEST_SHIFT_PARAMS.copy()
#     BAD_END["actual_start"] = "16:00"
#     BAD_END["actual_end"] = "08:00"
#     transport = ASGITransport(app=app)

#     async with AsyncClient(
#         transport=transport,
#         base_url=BASE_URL,
#     ) as client:
#         response = await client.post(
#             "/shifts",
#             params=BAD_END,
#         )

#     assert response.status_code == 400
#     data = response.json()
#     assert data["detail"] == "Actual shift end must be after start"


# # @pytest.mark.asyncio
# # async def test_get_balance():

# #     transport = ASGITransport(app=app)

# #     async with AsyncClient(
# #         transport=transport,
# #         base_url=BASE_URL,
# #     ) as client:
# #         response = await client.get(
# #             "/balance",
# #             params={"user_id": 1},
# #         )

# #     assert response.status_code == 200
# #     data = response.json()
# #     assert "balance_minutes" in data
# #     # Planned 08-16 (480 min)
# #     # Actual 08-17 (540 min)
# #     # Difference = +60
# #     assert data["balance_minutes"] == 60


# # @pytest.mark.asyncio
# # async def test_get_balance_unknown_user():

# #     transport = ASGITransport(app=app)

# #     async with AsyncClient(
# #         transport=transport,
# #         base_url=BASE_URL,
# #     ) as client:
# #         response = await client.get(
# #             "/balance",
# #             params={"user_id": 999},
# #         )

# #     assert response.status_code == 404
# #     data = response.json()
# #     assert data["detail"] == "User not found"


# # @pytest.mark.asyncio
# # async def test_get_balance_empty_user():

# #     transport = ASGITransport(app=app)

# #     async with AsyncClient(
# #         transport=transport,
# #         base_url=BASE_URL,
# #     ) as client:
# #         await client.post(
# #             "/users",
# #             params={"name": "Bob"},
# #         )

# #         response = await client.get(
# #             "/balance",
# #             params={"user_id": 2},
# #         )

# #     data = response.json()

# #     assert response.status_code == 200
# #     assert data["balance_minutes"] == 0


# # @pytest.mark.asyncio
# # async def test_get_balance_calculated():

# #     transport = ASGITransport(app=app)

# #     async with AsyncClient(
# #         transport=transport,
# #         base_url=BASE_URL,
# #     ) as client:
# #         response = await client.get(
# #             "/balance",
# #             params={"user_id": 1},
# #         )

# #     data = response.json()

# #     assert response.status_code == 200
# #     assert "balance_minutes" in data
# #     assert data["user_id"] == 1


# @pytest.mark.asyncio
# async def test_get_shifts():
#     transport = ASGITransport(app=app)
#     async with AsyncClient(
#         transport=transport,
#         base_url=BASE_URL,
#     ) as client:
#         response = await client.get(
#             "/shifts",
#             params={"user_id": TEST_SHIFT_PARAMS["user_id"]},
#         )

#     assert response.status_code == 200
#     data = response.json()
#     assert isinstance(data, list)
#     assert isinstance(data[0], dict)
#     assert len(data) >= 1
#     data = data[0]
#     assert data["date"] == TEST_SHIFT_PARAMS["date"]
#     assert (
#         data["actual"]
#         == f"{TEST_SHIFT_PARAMS['actual_start']}-{TEST_SHIFT_PARAMS['actual_end']}"
#     )
#     assert data["note"] == TEST_SHIFT_PARAMS["note"]


# @pytest.mark.asyncio
# async def test_delete_shift():
#     transport = ASGITransport(app=app)
#     async with AsyncClient(
#         transport=transport,
#         base_url=BASE_URL,
#     ) as client:
        
#         response = await client.delete("/shifts/3")
#         assert response.status_code == 200
#         data = response.json()
#         assert data["status"] == "deleted"

#         response = await client.get(
#             "/shifts",
#             params={"user_id": TEST_SHIFT_PARAMS["user_id"]},
#         )
#         print(response.json())
#         # assert len(response.json()) == 0


# # @pytest.mark.asyncio
# # async def test_update_shift_not_found():

# #     transport = ASGITransport(app=app)

# #     async with AsyncClient(
# #         transport=transport,
# #         base_url=BASE_URL,
# #     ) as client:
# #         response = await client.put(
# #             "/shifts/999",
# #             json={
# #                 "planned_start": "08:00",
# #                 "planned_end": "16:00",
# #                 "actual_start": "08:00",
# #                 "actual_end": "16:00",
# #                 "latest_child_name": "Test",
# #                 "latest_child_time": "15:00",
# #                 "note": "",
# #             },
# #         )

# #     assert response.status_code == 404


# # @pytest.mark.asyncio
# # async def test_delete_shift_not_found():

# #     transport = ASGITransport(app=app)

# #     async with AsyncClient(
# #         transport=transport,
# #         base_url=BASE_URL,
# #     ) as client:
# #         response = await client.delete("/shifts/999")

# #     assert response.status_code == 404


# # @pytest.mark.asyncio
# # async def test_get_shifts_empty_user():

# #     transport = ASGITransport(app=app)

# #     async with AsyncClient(
# #         transport=transport,
# #         base_url=BASE_URL,
# #     ) as client:
# #         response = await client.get(
# #             "/shifts",
# #             params={"user_id": 999},
# #         )

# #     assert response.status_code == 200
# #     assert response.json() == []


# # @pytest.mark.asyncio
# # async def test_current_period():

# #     transport = ASGITransport(app=app)

# #     async with AsyncClient(
# #         transport=transport,
# #         base_url=BASE_URL,
# #     ) as client:
# #         response = await client.get(
# #             "/current-period",
# #             params={"user_id": 1},
# #         )

# #     assert response.status_code == 200

# #     data = response.json()

# #     assert "period_start" in data
# #     assert "period_end" in data
# #     assert "shifts" in data
# #     assert isinstance(data["shifts"], list)
# #     assert data["period_start"] <= data["period_end"]
