import pytest
from app.schema.token import TokenValidationResponse
from app.dependacy.authenticate_user import AuthenticateUser
from app.model.user_profile import UserProfile
from app.main import app


@pytest.mark.asyncio
async def test_get_user_unauthenticated(client):
    # Do not override auth dependency - expect HTTPBasic to reject
    response = await client.get("/user")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_user_authenticated_with_record(client, db_session, monkeypatch):
    # Create a user in DB
    user = UserProfile(username="sarah", first_name="Sarah", last_name="Tester", mobile_number="+97312345678", is_mobile_number_verified=False, email_address="alice@example.com", is_email_address_verified=False)
    db_session.add(user)
    await db_session.commit()

    # Override auth dependency to return alice
    test_user = TokenValidationResponse(successful=True, username="sarah")
    async def _override_auth():
        return test_user

    monkeypatch.setitem(app.dependency_overrides, AuthenticateUser.get_logged_in_user, _override_auth)

    # Call the service
    response = await client.get("/user")
    assert response.status_code == 200
    body = response.json()
    # Should return populated profile
    assert body.get("username") == "sarah" or body.get("user_profile_info", {}).get("username") == "sarah"


@pytest.mark.asyncio
async def test_get_user_authenticated_without_record(client, monkeypatch):
    # Ensure no user in DB for ahmed
    # Override auth dependency to return ahmed
    test_user = TokenValidationResponse(successful=True, username="ahmed")

    async def _override_auth():
        return test_user

    monkeypatch.setitem(app.dependency_overrides, AuthenticateUser.get_logged_in_user, _override_auth)

    # Act
    response = await client.get("/user")
    assert response.status_code == 200
    body = response.json()
    # When no record exists, controller returns empty fields (nulls). Accept None or missing.
    # Check username is null/None or missing
    username = body.get("username") if isinstance(body, dict) else None
    # also support earlier schema where wrapper used `user_profile_info`
    if username is None and isinstance(body, dict) and body.get("user_profile_info"):
        username = body["user_profile_info"].get("username")

    assert username is None
