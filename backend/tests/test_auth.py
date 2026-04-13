"""Tests for auth endpoints: register, login, /auth/me."""


class TestRegister:
    def test_register_success(self, client):
        resp = client.post(
            "/api/v1/auth/register",
            json={"email": "new@example.com", "password": "secret123"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["access_token"]
        assert data["user"]["email"] == "new@example.com"
        assert "password" not in data["user"]

    def test_register_duplicate_email(self, client):
        email = "dupe@example.com"
        client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "password123"},
        )
        resp = client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "password456"},
        )
        assert resp.status_code == 409

    def test_register_normalizes_email(self, client):
        resp = client.post(
            "/api/v1/auth/register",
            json={"email": "  UPPER@Example.COM  ", "password": "secret123"},
        )
        assert resp.status_code == 201
        assert resp.json()["user"]["email"] == "upper@example.com"


class TestLogin:
    def test_login_success(self, client, registered_user):
        resp = client.post(
            "/api/v1/auth/login",
            json={
                "email": registered_user["email"],
                "password": registered_user["password"],
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["access_token"]
        assert data["user"]["email"] == registered_user["email"]

    def test_login_wrong_password(self, client, registered_user):
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": registered_user["email"], "password": "wrong"},
        )
        assert resp.status_code == 401

    def test_login_nonexistent_email(self, client):
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "nobody@example.com", "password": "secret"},
        )
        assert resp.status_code == 401


class TestAuthMe:
    def test_me_authenticated(self, client, registered_user, auth_headers):
        resp = client.get("/api/v1/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["email"] == registered_user["email"]

    def test_me_no_token(self, client):
        resp = client.get("/api/v1/auth/me")
        assert resp.status_code == 401

    def test_me_invalid_token(self, client):
        resp = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid.token.value"},
        )
        assert resp.status_code == 401
