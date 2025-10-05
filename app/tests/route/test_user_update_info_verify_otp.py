import pytest
from app.schema.token import TokenValidationResponse
from app.helper.otp_helper import OTPHelper
from app.main import app
import app.dependacy.redis_database as rdb
from app.model.user_profile import UserProfile
from app.repository.otp_repo import OTPRepository
import app.dependacy.redis_database as rdb
from app.dependacy.authenticate_user import AuthenticateUser
from app.dependacy.redis_database import redis_pool


@pytest.mark.asyncio
async def test_update_email_invalid_format(client, monkeypatch):
    # Override Keycloak token generation and user authentication
    test_user = TokenValidationResponse(successful=True, username="user1")
    async def _auth():
        return test_user
    monkeypatch.setitem(app.dependency_overrides, AuthenticateUser.get_logged_in_user, _auth)

    # send invalid email
    resp = await client.patch("/user", json={"email": "invalid-email"})
    assert resp.status_code == 422

@pytest.mark.asyncio
async def test_update_mobile_invalid_format(client, monkeypatch):
    # Override Keycloak token generation and user authentication
    test_user = TokenValidationResponse(successful=True, username="user2")
    async def _auth():
        return test_user
    monkeypatch.setitem(app.dependency_overrides, AuthenticateUser.get_logged_in_user, _auth)

    # Send invalid mobile that doesn't match +973XXXXXXXX
    resp = await client.patch("/user", json={"mobile": "12345"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_update_valid_email_and_mobile_schedules_otps(client, db_session, monkeypatch):
    # Create user in DB
    user = UserProfile(username="user3", first_name="U", last_name="3", mobile_number="+97311111111", is_mobile_number_verified=False, email_address="old@example.com", is_email_address_verified=False)
    db_session.add(user)
    await db_session.commit()

    # Override Keycloak token generation and user authentication
    test_user = TokenValidationResponse(successful=True, username="user3")
    async def _auth():
        return test_user
    monkeypatch.setitem(app.dependency_overrides, AuthenticateUser.get_logged_in_user, _auth)

    # Act as if email and sms were sent
    monkeypatch.setattr("app.controller.user_profile.EmailHelper.send_email_otp", lambda *a, **k: None)
    monkeypatch.setattr("app.controller.user_profile.SMSHelper.send_sms_otp", lambda *a, **k: None)

    # Request update
    new_email = "new@example.com"
    new_mobile = "+97322222222"
    resp = await client.patch("/user", json={"email": new_email, "mobile": new_mobile})
    assert resp.status_code == 200
    body = resp.json()
    assert body["successful"] is True
    assert body["email_update_requested"] is True
    assert body["mobile_update_requested"] is True


@pytest.mark.asyncio
async def test_enter_valid_email_otp_and_verify_changes(client, db_session, monkeypatch):
    # Arrange: create user and schedule OTP in redis via repository
    

    user = UserProfile(username="user4", first_name="U", last_name="Four", mobile_number="+97333333333", is_mobile_number_verified=False, email_address="old4@example.com", is_email_address_verified=False)
    db_session.add(user)
    await db_session.commit()

    # Override Keycloak token generation and user authentication
    test_user = TokenValidationResponse(successful=True, username="user4")
    from app.dependacy.authenticate_user import AuthenticateUser
    async def _auth():
        return test_user
    monkeypatch.setitem(app.dependency_overrides, AuthenticateUser.get_logged_in_user, _auth)

    # Put OTP into redis using OTPRepository
    otp = OTPHelper.generate_otp()
    new_email = "verified4@example.com"
    
    if getattr(rdb, "redis_pool", None) is None:
        await rdb.create_redis_db_pool()
    await OTPRepository.store_email_otp(rdb.redis_pool, "user4", new_email, otp)

    # Act: confirm OTP
    resp = await client.post("/user/verify-otp", json={"otp": otp, "otp_type": "email"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["successful"] is True

    # Check /user reflects updated email
    resp2 = await client.get("/user")
    assert resp2.status_code == 200
    body2 = resp2.json()
    # Accept either top-level user_profile_info or direct fields
    username = body2.get("user_profile_info", {}).get("username") if body2.get("user_profile_info") else body2.get("username")
    assert username == "user4"
    # Check the email is updated/verified
    email_val = body2.get("user_profile_info", {}).get("email") if body2.get("user_profile_info") else body2.get("email")
    assert email_val == new_email


@pytest.mark.asyncio
async def test_enter_valid_mobile_otp_and_verify_changes(client, db_session, monkeypatch):
    # Create user in DB
    user = UserProfile(username="user5", first_name="U5", last_name="Five", mobile_number="+97344444444", is_mobile_number_verified=False, email_address="old5@example.com", is_email_address_verified=False)
    db_session.add(user)
    await db_session.commit()

    # Override Keycloak token generation and user authentication
    test_user = TokenValidationResponse(successful=True, username="user5")
    from app.dependacy.authenticate_user import AuthenticateUser
    async def _auth():
        return test_user
    monkeypatch.setitem(app.dependency_overrides, AuthenticateUser.get_logged_in_user, _auth)

    # Put OTP into redis
    otp = OTPHelper.generate_otp()
    new_mobile = "+97355555555"
    if getattr(rdb, "redis_pool", None) is None:
        await rdb.create_redis_db_pool()
    await OTPRepository.store_sms_otp(rdb.redis_pool, "user5", new_mobile, otp)

    # Confirm mobile OTP
    resp = await client.post("/user/verify-otp", json={"otp": otp, "otp_type": "mobile"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["successful"] is True

    # Check /user reflects updated mobile
    resp2 = await client.get("/user")
    assert resp2.status_code == 200
    body2 = resp2.json()
    # Check mobile updated
    mobile_val = body2.get("user_profile_info", {}).get("mobile") if body2.get("user_profile_info") else body2.get("mobile")
    assert mobile_val == new_mobile
