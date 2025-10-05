import pytest
import asyncio
from httpx import AsyncClient
from app.main import app
from app.schema.token import TokenValidationResponse


@pytest.mark.asyncio
async def test_create_user_success(client, db_session, monkeypatch):
    # Arrange: override authentication dependency to return a test user
    test_user = TokenValidationResponse(successful=True, username="testuser")
    # Override the FastAPI dependency to bypass HTTPBasic security
    from app.dependacy.authenticate_user import AuthenticateUser
    async def _override_auth():
        return test_user
    monkeypatch.setitem(app.dependency_overrides, AuthenticateUser.get_logged_in_user, _override_auth)

    # Monkeypatch KeycloakHelper to return an object with necessary fields
    class KCUser:
        def __init__(self):
            self.id = "kc-id-1"
            self.username = "testuser"
            self.first_name = "Test"
            self.last_name = "User"
            self.mobile = "1234567890"
            self.mobile_verified = False
            self.email = "test@example.com"
            self.email_verified = False

    async def _kc(username):
        return KCUser()

    monkeypatch.setattr(
        "app.controller.user_profile.KeycloakHelper.return_matching_user_info",
        _kc,
    )

    # Act
    resp = await client.post("/user")

    # Assert
    assert resp.status_code == 200
    body = resp.json()
    assert body["successful"] is True
    # schema uses `user_profile_info` as the payload key
    assert body["user_profile_info"]["username"] == "testuser"


@pytest.mark.asyncio
async def test_create_user_duplicate(client, db_session, monkeypatch):
    # Arrange: override authentication dependency to return a test user
    test_user = TokenValidationResponse(successful=True, username="dupuser")
    # Override the FastAPI dependency to bypass HTTPBasic security
    from app.dependacy.authenticate_user import AuthenticateUser
    async def _override_auth():
        return test_user
    monkeypatch.setitem(app.dependency_overrides, AuthenticateUser.get_logged_in_user, _override_auth)

    # Monkeypatch KeycloakHelper to return an object with necessary fields
    class KCUser:
        def __init__(self):
            self.id = "kc-id-2"
            self.username = "dupuser"
            self.first_name = "Dup"
            self.last_name = "User"
            self.mobile = "5555555555"
            self.mobile_verified = False
            self.email = "dup@example.com"
            self.email_verified = False

    async def _kc(username):
        return KCUser()

    monkeypatch.setattr(
        "app.controller.user_profile.KeycloakHelper.return_matching_user_info",
        _kc,
    )

    # Pre-insert a user into the database to simulate duplicate
    from app.model.user_profile import UserProfile
    user = UserProfile(username="dupuser", first_name="Dup", last_name="User", mobile_number="5555555555", is_mobile_number_verified=False, email_address="dup@example.com", is_email_address_verified=False)
    db_session.add(user)
    await db_session.commit()

    # Act
    resp = await client.post("/user")

    # Assert: creation should fail due to existing user
    assert resp.status_code == 200
    body = resp.json()
    assert body["successful"] is False
