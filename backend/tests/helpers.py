def assert_ok(response):
    assert response.status_code == 200
    return response.json()


def assert_invalid_credentials(response):
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"
