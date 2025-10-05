from fastapi import APIRouter,Depends
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as aioredis
from app.dependacy.authenticate_user import AuthenticateUser
from app.schema.token import TokenValidationResponse
from app.schema.user import UserProfileInfoResponse,UpdateUserInfo,UpdateUserInfoResponse
from app.schema.otp import SendOTPSchema,OTPVerificationResponse
from app.schema.totp import SendTOTP,TOTPGenerationResult,TOTPVerificationResult
from app.dependacy.pg_database import get_pg_db_connection
from app.dependacy.redis_database import get_redis_db_client
from app.controller.user_profile import UserProfileController

user_router = APIRouter()

@user_router.post('/user')
async def create_user_profile(authentication_results: TokenValidationResponse=Depends(AuthenticateUser.get_logged_in_user),
                              db:AsyncSession=Depends(get_pg_db_connection))->UserProfileInfoResponse:
    """Create a user profile."""
    return await UserProfileController.create_user_profile(authentication_results,db)

@user_router.get('/user')
async def get_user_profile(authentication_results: TokenValidationResponse=Depends(AuthenticateUser.get_logged_in_user),
                              db:AsyncSession=Depends(get_pg_db_connection)):
    return await UserProfileController.get_user_profile(authentication_results,db)

@user_router.patch('/user')
async def update_user_profile(updated_user_info:UpdateUserInfo,authentication_results: TokenValidationResponse=Depends(AuthenticateUser.get_logged_in_user),
                              db:AsyncSession=Depends(get_pg_db_connection),redis:aioredis.Redis=Depends(get_redis_db_client))->UpdateUserInfoResponse:
    return await UserProfileController.update_user_info(authentication_results,updated_user_info,db,redis)

@user_router.post('/user/verify-otp')
async def verify_otp(received_otp:SendOTPSchema,authentication_results: TokenValidationResponse=Depends(AuthenticateUser.get_logged_in_user),
                              db:AsyncSession=Depends(get_pg_db_connection),redis:aioredis.Redis=Depends(get_redis_db_client))->OTPVerificationResponse:
    return await UserProfileController.verify_otp(authentication_results,received_otp,db,redis)

@user_router.post('/user/generate-totp')
async def generate_totp(authentication_results: TokenValidationResponse=Depends(AuthenticateUser.get_logged_in_user),
                              db:AsyncSession=Depends(get_pg_db_connection),redis:aioredis.Redis=Depends(get_redis_db_client))->TOTPGenerationResult:
    return await UserProfileController.generate_totp_seed(authentication_results,db,redis)

@user_router.post('/user/verify-totp')
async def verify_totp(received_totp:SendOTPSchema,authentication_results: TokenValidationResponse=Depends(AuthenticateUser.get_logged_in_user),
                              db:AsyncSession=Depends(get_pg_db_connection),redis:aioredis.Redis=Depends(get_redis_db_client))->TOTPVerificationResult:
    return await UserProfileController.verify_totp_seed(authentication_results,received_totp.otp,received_totp.otp_type,db,redis)