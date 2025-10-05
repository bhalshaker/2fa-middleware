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
async def create_user_profile(received_token: TokenValidationResponse=Depends(AuthenticateUser.get_logged_in_user),
                              db:AsyncSession=Depends(get_pg_db_connection))->UserProfileInfoResponse:
    return await UserProfileController.create_user_profile(received_token,db)

@user_router.get('/user')
async def get_user_profile(received_token: TokenValidationResponse=Depends(AuthenticateUser.get_logged_in_user),
                              db:AsyncSession=Depends(get_pg_db_connection)):
    return await UserProfileController.get_user_profile(received_token,db)

@user_router.patch('/user')
async def update_user_profile(updated_user_info:UpdateUserInfo,received_token: TokenValidationResponse=Depends(AuthenticateUser.get_logged_in_user),
                              db:AsyncSession=Depends(get_pg_db_connection),redis:aioredis.Redis=Depends(get_redis_db_client))->UpdateUserInfoResponse:
    return await UserProfileController.update_user_info(received_token,updated_user_info,db,redis)

@user_router.post('/user/verify-otp')
async def verify_otp(received_otp:SendOTPSchema,received_token: TokenValidationResponse=Depends(AuthenticateUser.get_logged_in_user),
                              db:AsyncSession=Depends(get_pg_db_connection),redis:aioredis.Redis=Depends(get_redis_db_client))->OTPVerificationResponse:
    return await UserProfileController.verify_otp(received_token,received_otp,db,redis)

@user_router.post('/user/generate-totp')
async def generate_totp(received_token: TokenValidationResponse=Depends(AuthenticateUser.get_logged_in_user),
                              db:AsyncSession=Depends(get_pg_db_connection),redis:aioredis.Redis=Depends(get_redis_db_client))->TOTPGenerationResult:
    return await UserProfileController.generate_totp_seed(received_token,db,redis)

@user_router.post('/user/verify-totp')
async def verify_totp(received_totp:SendOTPSchema,received_token: TokenValidationResponse=Depends(AuthenticateUser.get_logged_in_user),
                              db:AsyncSession=Depends(get_pg_db_connection),redis:aioredis.Redis=Depends(get_redis_db_client))->TOTPVerificationResult:
    return await UserProfileController.verify_totp_seed(received_token,received_totp.otp,received_totp.otp_type,db,redis)