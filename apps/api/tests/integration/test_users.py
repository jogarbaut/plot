import pytest
from fastapi.testclient import TestClient
from unittest.mock import ANY

from app.core.auth import verify_token
from app.core.database import get_db
from app.main import app

AUTH0_ID = "auth0|test-user-123"
OTHER_AUTH0_ID = "auth0|other-user-456"

USER_PAYLOAD = {
    "email": "jomel@example.com",
    "username": "jomel",
    "first_name": "Jomel",
    "last_name": "Bautista",
    "birthday": "1995-06-15",
}


def _override_token(auth0_id: str = AUTH0_ID):
    return lambda: {"sub": auth0_id}


@pytest.fixture()
def client(db):
    app.dependency_overrides[verify_token] = _override_token()
    app.dependency_overrides[get_db] = lambda: (yield db)
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def registered_client(db):
    app.dependency_overrides[verify_token] = _override_token()
    app.dependency_overrides[get_db] = lambda: (yield db)
    client = TestClient(app)
    client.post("/users", json=USER_PAYLOAD)
    yield client
    app.dependency_overrides.clear()


class TestCreateUser:
    def test_creates_user_and_returns_201(self, client):
        response = client.post("/users", json=USER_PAYLOAD)

        assert response.status_code == 201
        assert response.json() == {
            "id": ANY,
            "auth0_id": AUTH0_ID,
            "email": USER_PAYLOAD["email"],
            "username": USER_PAYLOAD["username"],
            "first_name": USER_PAYLOAD["first_name"],
            "last_name": USER_PAYLOAD["last_name"],
            "birthday": USER_PAYLOAD["birthday"],
            "avatar_url": None,
            "created_at": ANY,
            "updated_at": ANY,
        }

    def test_returns_409_if_auth0_id_already_registered(self, client):
        client.post("/users", json=USER_PAYLOAD)

        response = client.post("/users", json={**USER_PAYLOAD, "email": "other@example.com", "username": "other"})

        assert response.status_code == 409

    def test_returns_409_if_email_already_taken(self, registered_client):
        app.dependency_overrides[verify_token] = _override_token(OTHER_AUTH0_ID)

        response = registered_client.post("/users", json={**USER_PAYLOAD, "username": "different"})

        assert response.status_code == 409

    def test_returns_409_if_username_already_taken(self, registered_client):
        app.dependency_overrides[verify_token] = _override_token(OTHER_AUTH0_ID)

        response = registered_client.post("/users", json={**USER_PAYLOAD, "email": "different@example.com"})

        assert response.status_code == 409


class TestGetMe:
    def test_returns_profile_for_registered_user(self, registered_client):
        response = registered_client.get("/users/me")

        assert response.status_code == 200
        assert response.json()["username"] == USER_PAYLOAD["username"]

    def test_returns_404_if_user_not_registered(self, client):
        response = client.get("/users/me")

        assert response.status_code == 404
