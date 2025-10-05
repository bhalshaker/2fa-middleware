from app.model.user_profile import UserProfile
from app.repository.user_repo import UserRepository
from app.repository.totp_repo import TOTPRepository
from app.repository.otp_repo import OTPRepository
from app.schema.token import TokenValidationResponse
from app.schema.totp import SeedFullInfo,TOTPVerificationResult,TOTPGenerationResult
from app.schema.user import UserProfileInfo,UpdateUserInfo,UpdateUserInfoResponse,UserProfileInfoResponse
from app.schema.otp import OTPVerificationResponse,SendOTPSchema
from app.helper.keycloak_helper import KeycloakHelper
from app.helper.totp_helper import TOTPHelper
from app.helper.otp_helper import OTPHelper
from app.helper.email_helper import EmailHelper
from app.helper.sms_helper import SMSHelper
from app.exception.exceptions import (NoMatchingUserError,NoMatchingOTPError,NoMatchingSeedError,
                                      SeedWaitingForConfirmationError,TechnicalError,MatchingUserError,
                                      ExistingOTPError)
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import BackgroundTasks,Depends
import redis.asyncio as aioredis
import logging

class UserProfileController:

    logger=logging.getLogger(__name__)

    @staticmethod
    async def create_user_profile(authentication_results: TokenValidationResponse,db:AsyncSession) -> UserProfileInfoResponse:
        """Create a new user profile in the database if one does not already exist.
        Args:
            authentication_results (TokenValidationResponse): The validated token containing user information.
            db (AsyncSession): The database session for performing operations.
        Returns:
            UserProfileInfoResponse: The created user profile information.
        """
        try:
            # Make sure there is no existing record for this user in the database
            UserProfileController.logger.info(f"# Looking for a matching record for user {authentication_results.username}")
            user_profile=await UserRepository.get_user_by_username(authentication_results.username,db)
            if user_profile:
                raise MatchingUserError() # Return user creation failed because user already exists
            UserProfileController.logger.info(f"# Good news no record for :{authentication_results.username}")
            # Get user attributes from keycloak
            user_attributes=await KeycloakHelper.return_matching_user_info(authentication_results.username)
            UserProfileController.logger.info(f"# {authentication_results.username} Attributes were retrieved from keycloak")
            if user_attributes.id==None:
                raise NoMatchingUserError()
            # Create a new profile record
            user_profile=UserProfile(
                                        username=user_attributes.username,
                                        first_name=user_attributes.first_name,
                                        last_name=user_attributes.last_name,
                                        mobile_number= user_attributes.mobile,
                                        is_mobile_number_verified=user_attributes.mobile_verified,
                                        email_address=user_attributes.email,
                                        is_email_address_verified=user_attributes.email_verified
                                    )
            UserProfileController.logger.info(f"# Creating the following record {user_profile}")
            refreshed_user_profile=await UserRepository.create_new_user(user_profile,db)
            # Return refreshed data (construct Pydantic models with keyword args)
            return UserProfileInfoResponse(
                successful=True,
                message="",
                data=UserProfileInfo(
                    username=refreshed_user_profile.username,
                    first_name=refreshed_user_profile.first_name,
                    last_name=refreshed_user_profile.last_name,
                    mobile=refreshed_user_profile.mobile_number,
                    mobile_verified=refreshed_user_profile.is_mobile_number_verified,
                    email=refreshed_user_profile.email_address,
                    email_verified=refreshed_user_profile.is_email_address_verified,
                ),
            )
        except Exception as exc:
            UserProfileController.logger.error(str(exc))
            # Return user profile info with null values using keyword args
            return UserProfileInfoResponse(successful=False, message=str(exc))
    @staticmethod
    async def get_user_profile(authentication_results: TokenValidationResponse,db:AsyncSession)->UserProfileInfo|None:
        user_info=UserProfileInfo()
        user= await UserRepository.get_user_by_username(authentication_results.username,db)
        if user:
                user_info=UserProfileInfo(username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    mobile=user.mobile_number,
                    mobile_verified=user.is_mobile_number_verified,
                    email=user.email_address,
                    email_verified=user.is_email_address_verified,)
        return user_info
        
    # Generate TOTP
    @staticmethod
    async def generate_totp_seed(authentication_results: TokenValidationResponse,db:AsyncSession,redis:aioredis.Redis)->TOTPGenerationResult:
        """Generate a TOTP seed for the user.
        Args:
            authentication_results (TokenValidationResponse): The token validation response containing user information.
            db (AsyncSession): The database session for performing operations.
            redis (aioredis.Redis): The Redis instance for caching and OTP storage.
        Returns:
            TOTPGenerationResult: The response containing the result of the TOTP generation.
        """
        try:
            user_profile=await UserRepository.get_user_by_username(authentication_results.username,db)
            if not(user_profile):
                raise NoMatchingUserError() # indicate that this can not be done because there are not records for user in our db
            # Is there is a current token
            current_token=await TOTPRepository.get_totp_seed(redis,authentication_results.username)
            if current_token:
                raise SeedWaitingForConfirmationError() # Return an error wait for x minutes before trying again
            # Generate totp for the user
            totp_info=TOTPHelper.generate_seed_with_uri_image(authentication_results.username)
            # Store totp in Redis
            successful_seed_insertion=await TOTPRepository.store_totp_seed(redis,authentication_results.username,totp_info.seed)
            if not(successful_seed_insertion):
                raise TechnicalError() # Return and error seed can not be inserted
            return TOTPGenerationResult(successful=True,message="",data=totp_info)
        except Exception as exc:
            return TOTPGenerationResult(successful=False,message=str(exc),data=None)
    
    @staticmethod
    async def verify_totp_seed(authentication_results: TokenValidationResponse,totp:str,new_seed:bool,db:AsyncSession,redis:aioredis.Redis)->TOTPVerificationResult:
        """Verify the TOTP for the user.
        Args:
            authentication_results (TokenValidationResponse): The token validation response containing user information.
            totp (str): The TOTP code sent by the user.
            new_seed (bool): Flag indicating if this is a new seed verification.
            db (AsyncSession): The database session for performing operations.
            redis (aioredis.Redis): The Redis instance for caching and OTP storage.
        Returns:
            TOTPVerificationResult: The response containing the result of the TOTP verification.
        """
        try:
            # Fetch current user profile
            user_profile=await UserRepository.get_user_by_username(authentication_results.username,db)
            # If user does not exist flag operation as failed
            if not(user_profile):
                return NoMatchingUserError # indicate that this can not be done because there are not records for user in our db
            # Is the request to verify a new seed
            if new_seed:
                # Is there is a current new seed
                current_seed=await TOTPRepository.get_totp_seed(redis,authentication_results.username)
                # If there is no current seed return an error
                if not(current_seed):
                    return NoMatchingSeedError # Return an error wait for x minutes before trying again
                # Verify the totp and if it is valid delete the seed from redis and update user profile
                if TOTPHelper.verify_totp(current_seed,totp):
                    await TOTPRepository.delete_totp_seed(redis,authentication_results.username)
                    encoded_seed=TOTPHelper.encrypt_seed(current_seed)
                    user_profile=await UserRepository.update_user_totp(authentication_results.username,encoded_seed,db)
                    return TOTPVerificationResult(successful=True,message=None)
                else:
                    return TOTPVerificationResult(successful=False,message="Invalid TOTP for the new seed.")
            # If it is not a new seed verification then check if user has a seed and verify it
            else:
                decoded_seed=TOTPHelper.decrypt_seed(user_profile.totp_secret_encrypted)
                return TOTPVerificationResult(successful=TOTPHelper.verify_totp(decoded_seed,totp),message=None)
        except Exception as exc:
            return TOTPVerificationResult(successful=False,message=str(exc))

    @staticmethod
    async def update_user_info(authentication_results: TokenValidationResponse,updated_user_info:UpdateUserInfo,db:AsyncSession,
                               redis:aioredis.Redis,background_tasks: BackgroundTasks)->UpdateUserInfoResponse:
        """Update user information such as email and mobile number.
        Args:
            authentication_results (TokenValidationResponse): The token validation response containing user information.
            updated_user_info (UpdateUserInfo): The new user information to be updated.
            db (AsyncSession): The database session for performing operations.
            redis (aioredis.Redis): The Redis client for OTP storage.
            background_tasks (BackgroundTasks): FastAPI BackgroundTasks instance for sending emails/SMS.
        Returns:
            UpdateUserInfoResponse: The response indicating the result of the update operation.
        """
        # Initialize response
        update_response=UpdateUserInfoResponse(successful=False)
        try:
            # Fetch current user profile
            user_profile=await UserRepository.get_user_by_username(authentication_results.username,db)
            # If user does not exist flag operation as failed
            if not(user_profile):
                raise NoMatchingUserError()
            # Check for email changes and send OTP if changed
            if updated_user_info.email and (updated_user_info.email!=user_profile.email_address):
                UserProfileController.logger.info(f"# newly requested email update for User {authentication_results.username} is allowed")
                has_existing_otp=await OTPRepository.user_has_existing_otp_by_otp_type(redis,authentication_results.username,'email')
                if has_existing_otp:
                    raise ExistingOTPError()
                # Create OTP
                generated_otp=OTPHelper.generate_otp()
                # Store OTP in Redis
                await OTPRepository.store_email_otp(redis,user_profile.username,updated_user_info.email,generated_otp)
                UserProfileController.logger.info(f"Email OTP for user {user_profile.username} stored in Redis")
                # Send OTP via email in the background
                background_tasks.add_task(EmailHelper.send_email_otp,updated_user_info.email,user_profile.last_name,generated_otp)
                UserProfileController.logger.info(f"Email OTP for user {user_profile.username} is scheduled to be sent")
                # Flag email update as requested
                update_response.successful=True
                update_response.email_update_requested=True
            # If email is same as before flag that no update is requested
            elif updated_user_info.email and (updated_user_info.email==user_profile.email_address):
                UserProfileController.logger.info(f"# newly requested email update for User {authentication_results.username} not allowed")
                # Create OTP
                update_response.email_update_requested=False
            # Check for mobile changes and send OTP if changed
            if updated_user_info.mobile and (updated_user_info.mobile!=user_profile.mobile_number):
                UserProfileController.logger.info(f"# newly requested mobile update for User {authentication_results.username} is allowed")
                has_existing_otp=await OTPRepository.user_has_existing_otp_by_otp_type(redis,authentication_results.username,'mobile')
                if has_existing_otp:
                    raise ExistingOTPError()
                # Create OTP
                generated_otp=OTPHelper.generate_otp()
                # Store OTP in Redis
                await OTPRepository.store_sms_otp(redis,user_profile.username,updated_user_info.mobile,generated_otp)
                UserProfileController.logger.info(f"Mobile OTP for user {user_profile.username} stored in Redis")
                # Send OTP via SMS in the background
                update_response.successful=True
                background_tasks.add_task(SMSHelper.send_sms_otp,updated_user_info.mobile,user_profile.last_name,generated_otp)
                UserProfileController.logger.info(f"Mobile OTP for user {user_profile.username} is scheduled to be sent")
                update_response.mobile_update_requested=True
            # If mobile is same as before flag that no update is requested
            elif updated_user_info.mobile and (updated_user_info.mobile==user_profile.mobile_number):
                UserProfileController.logger.info(f"# newly requested mobile update for User {authentication_results.username} not allowed")
                update_response.mobile_update_requested=False
            return update_response
        except Exception as exc:
            UserProfileController.logger.error(f"{str(exc)}")
            # Flag operation as failed
            update_response.successful=False
            update_response.message=str(exc)
            return update_response

    # Verify OTP
    @staticmethod
    async def verify_otp(authentication_results: TokenValidationResponse,received_otp:SendOTPSchema,db:AsyncSession,redis:aioredis.Redis)->OTPVerificationResponse:
        """Verify the OTP for the user.

        Args:
            authentication_results (TokenValidationResponse): The token validation response containing user information.
            received_otp (SendOTPSchema): The OTP details sent by the user.
            db (AsyncSession): The database session for performing operations.
            redis (aioredis.Redis): The Redis instance for caching and OTP storage.
        Returns:
            OTPVerificationResponse: The response containing the result of the OTP verification.
        """
        # Initialize response
        verification_response=OTPVerificationResponse(successful=False)
        try:
            # Fetch current user profile
            user_profile=await UserRepository.get_user_by_username(authentication_results.username,db)
            # If user does not exist flag operation as failed
            if not(user_profile):
                raise NoMatchingUserError()
            #Look for a matching otp
            matching_otp_identifier=await OTPRepository.find_user_key_value_by_otp(redis,authentication_results.username,received_otp.otp,received_otp.otp_type)
            if not (matching_otp_identifier):
                raise NoMatchingOTPError()
            # Delete OTP
            await OTPRepository.confirm_and_delete_otp(redis,authentication_results.username,matching_otp_identifier,received_otp.otp,received_otp.otp_type)
            # Update user data based on type
            if received_otp.otp_type=="mobile":
                await UserRepository.update_user_mobile(authentication_results.username,matching_otp_identifier,db)
            elif received_otp.otp_type=="email":
                await UserRepository.update_user_email(authentication_results.username,matching_otp_identifier,db)
            # Flag operation as successful
            verification_response.successful=True
            return verification_response
        except Exception as exc:
            # Flag operation as failure
            verification_response.successful=False
            verification_response.message=str(exc)
            return verification_response

