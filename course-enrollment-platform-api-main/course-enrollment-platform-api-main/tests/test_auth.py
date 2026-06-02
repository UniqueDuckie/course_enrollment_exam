def test_register_creates_user(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "Alice",
            "email": "alice@x.com",
            "password": "password123",
            "role": "student",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "alice@x.com"
    assert body["role"] == "student"
    assert body["is_active"] is True
    assert "hashed_password" not in body


def test_register_rejects_duplicate_email(client):
    payload = {
        "name": "A",
        "email": "dup@x.com",
        "password": "password123",
        "role": "student",
    }
    assert client.post("/auth/register", json=payload).status_code == 201
    assert client.post("/auth/register", json=payload).status_code == 409


def test_register_validates_role(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "Bad",
            "email": "bad@x.com",
            "password": "password123",
            "role": "teacher",
        },
    )
    assert response.status_code == 422


def test_register_requires_valid_email(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "Bad",
            "email": "notanemail",
            "password": "password123",
            "role": "student",
        },
    )
    assert response.status_code == 422


def test_login_returns_token(client):
    client.post(
        "/auth/register",
        json={
            "name": "A",
            "email": "u@x.com",
            "password": "password123",
            "role": "student",
        },
    )
    response = client.post(
        "/auth/login", data={"username": "u@x.com", "password": "password123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_rejects_wrong_password(client):
    client.post(
        "/auth/register",
        json={
            "name": "A",
            "email": "u@x.com",
            "password": "password123",
            "role": "student",
        },
    )
    response = client.post(
        "/auth/login", data={"username": "u@x.com", "password": "wrong"}
    )
    assert response.status_code == 401


def test_login_rejects_unknown_user(client):
    response = client.post(
        "/auth/login", data={"username": "nobody@x.com", "password": "x"}
    )
    assert response.status_code == 401


def test_me_requires_auth(client):
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_me_returns_profile(client, student_token, auth_header):
    response = client.get("/auth/me", headers=auth_header(student_token))
    assert response.status_code == 200
    assert response.json()["email"] == "student@x.com"
