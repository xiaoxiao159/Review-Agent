def test_login_success(client):
    response = client.post("/api/v1/auth/login", json={"username": "admin", "password": "Admin@123456"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()


def test_login_invalid_password(client):
    response = client.post("/api/v1/auth/login", json={"username": "admin", "password": "bad-pass"})
    assert response.status_code == 401


def test_register_then_login(client):
    register = client.post(
        "/api/v1/auth/register",
        json={"username": "user1", "email": "user1@example.com", "password": "User@123456"},
    )
    assert register.status_code == 200

    login = client.post("/api/v1/auth/login", json={"username": "user1", "password": "User@123456"})
    assert login.status_code == 200


def test_me_requires_auth(client, auth_header):
    response = client.get("/api/v1/auth/me", headers=auth_header)
    assert response.status_code == 200
    assert response.json()["username"]


def test_refresh_and_logout_flow(client):
    login = client.post("/api/v1/auth/login", json={"username": "admin", "password": "Admin@123456"})
    refresh_token = login.json()["refresh_token"]

    refreshed = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert refreshed.status_code == 200

    logout = client.post("/api/v1/auth/logout", json={"refresh_token": refreshed.json()["refresh_token"]})
    assert logout.status_code == 200


def test_forgot_password_placeholder(client):
    response = client.post("/api/v1/auth/forgot-password", json={"email": "admin@example.com"})
    assert response.status_code == 200
