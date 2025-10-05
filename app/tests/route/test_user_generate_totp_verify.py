import pytest
from app.schema.token import TokenValidationResponse
from app.helper.totp_helper import TOTPHelper
from app.repository.totp_repo import TOTPRepository
from app.model.user_profile import UserProfile
import app.dependacy.redis_database as rdb
from app.dependacy.authenticate_user import AuthenticateUser
from app.main import app


@pytest.mark.asyncio
async def test_generate_and_verify_new_seed_success(client, db_session, monkeypatch):
    # Create user without totp
    user = UserProfile(username="guser1", first_name="G", last_name="One", mobile_number="+97390000001", is_mobile_number_verified=False, email_address="g1@example.com", is_email_address_verified=False)
    db_session.add(user)
    await db_session.commit()

    # Auth override
    test_user = TokenValidationResponse(successful=True, username="guser1")
    
    async def _auth():
        return test_user
    monkeypatch.setitem(app.dependency_overrides, AuthenticateUser.get_logged_in_user, _auth)

    # Ensure redis pool
    if getattr(rdb, "redis_pool", None) is None:
        await rdb.create_redis_db_pool()

    # Generate seed
    resp = await client.post("/user/generate-totp")
    assert resp.status_code == 200
    body = resp.json()
    assert body["successful"] is True
    seed = body["data"]["seed"] if body.get("data") else body.get("data") or body.get("user_profile_info")
    # If schema returns nested, try retrieve correctly
    if isinstance(seed, dict):
        seed = seed.get("seed")
    assert isinstance(seed, str) and len(seed) > 0

    # Compute current totp
    import pyotp
    totp_code = pyotp.TOTP(seed).now()

    # Verify new seed
    resp2 = await client.post("/user/verify-totp", json={"totp": totp_code, "is_new_seed": True})
    assert resp2.status_code == 200
    body2 = resp2.json()
    assert body2["successful"] is True

    # Confirm DB user got updated totp (encrypted) and is_totp_verified True
    refreshed = await db_session.get(UserProfile, user.id)
    assert refreshed.totp_secret_encrypted is not None
    assert refreshed.is_totp_verified is True


@pytest.mark.asyncio
async def test_generate_and_verify_new_seed_invalid_totp(client, db_session, monkeypatch):
    user = UserProfile(username="guser2", first_name="G", last_name="Two", mobile_number="+97390000002", is_mobile_number_verified=False, email_address="g2@example.com", is_email_address_verified=False)
    db_session.add(user)
    await db_session.commit()

    test_user = TokenValidationResponse(successful=True, username="guser2")
    
    async def _auth():
        return test_user
    monkeypatch.setitem(app.dependency_overrides, AuthenticateUser.get_logged_in_user, _auth)

    if getattr(rdb, "redis_pool", None) is None:
        await rdb.create_redis_db_pool()

    resp = await client.post("/user/generate-totp")
    assert resp.status_code == 200
    body = resp.json()
    seed = body["data"]["seed"] if body.get("data") else None
    import pyotp
    # craft an invalid totp (different from current)
    invalid_totp = "000000"
    if pyotp.TOTP(seed).now() == invalid_totp:
        invalid_totp = "111111"

    resp2 = await client.post("/user/verify-totp", json={"totp": invalid_totp, "is_new_seed": True})
    assert resp2.status_code == 200
    body2 = resp2.json()
    assert body2["successful"] is False


@pytest.mark.asyncio
async def test_existing_verified_seed_valid_totp(client, db_session, monkeypatch):
    # Create user with existing verified seed
    seed = TOTPHelper.generate_seed()
    encrypted = TOTPHelper.encrypt_seed(seed)
    user = UserProfile(username="guser3", first_name="G", last_name="Three", mobile_number="+97390000003", is_mobile_number_verified=False, email_address="g3@example.com", is_email_address_verified=False, totp_secret_encrypted=encrypted, is_totp_verified=True)
    db_session.add(user)
    await db_session.commit()

    test_user = TokenValidationResponse(successful=True, username="guser3")
    from app.dependacy.authenticate_user import AuthenticateUser
    async def _auth():
        return test_user
    monkeypatch.setitem(app.dependency_overrides, AuthenticateUser.get_logged_in_user, _auth)

    import pyotp
    totp_code = pyotp.TOTP(seed).now()

    resp = await client.post("/user/verify-totp", json={"totp": totp_code, "is_new_seed": False})
    assert resp.status_code == 200
    body = resp.json()
    assert body["successful"] is True


@pytest.mark.asyncio
async def test_existing_verified_seed_invalid_totp(client, db_session, monkeypatch):
    seed = TOTPHelper.generate_seed()
    encrypted = TOTPHelper.encrypt_seed(seed)
    user = UserProfile(username="guser4", first_name="G", last_name="Four", mobile_number="+97390000004", is_mobile_number_verified=False, email_address="g4@example.com", is_email_address_verified=False, totp_secret_encrypted=encrypted, is_totp_verified=True)
    db_session.add(user)
    await db_session.commit()

    test_user = TokenValidationResponse(successful=True, username="guser4")
    from app.dependacy.authenticate_user import AuthenticateUser
    async def _auth():
        return test_user
    monkeypatch.setitem(app.dependency_overrides, AuthenticateUser.get_logged_in_user, _auth)

    # invalid totp
    invalid = "000000"
    import pyotp
    if pyotp.TOTP(seed).now() == invalid:
        invalid = "111111"

    resp = await client.post("/user/verify-totp", json={"totp": invalid, "is_new_seed": False})
    assert resp.status_code == 200
    body = resp.json()
    assert body["successful"] is False
