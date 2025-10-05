from sqlalchemy.ext.asyncio import AsyncSession
from app.model.user_profile import UserProfile
from sqlalchemy.future import select
import logging

class UserRepository():
    """Repository for user profile related database operations."""

    logger=logging.getLogger(__name__)

    @staticmethod
    async def get_user_by_username(username:str,db: AsyncSession)->UserProfile | None:
        """
         Retrieve a user by username.
         Args:
            username (str): The username of the user to retrieve.
            db (AsyncSession): The database session. 
        Returns:
            UserProfile | None: The user profile if found, otherwise None.
        """
        result = await db.execute(select(UserProfile).where(UserProfile.username == username))
        return result.scalars().first()

    @staticmethod
    async def create_new_user(user_profile:UserProfile,db: AsyncSession)->UserProfile:
        """
         Create a new user.
         Args:
            user_profile (UserProfile): User profile info.
            db (AsyncSession): The database session. 
        Returns:
            UserProfile: Get refereshed user profile info.
        """
        db.add(user_profile)
        await db.commit()
        await db.refresh(user_profile)
        return user_profile

    @staticmethod
    async def update_user_totp(username:str,seed:str,db: AsyncSession)->UserProfile|None:
        """
        Update user totp.   
        Args:
            username (str): The username of the user to retrieve.
            seed (str): TOTP seed secret key
            db (AsyncSession): The database session.
        Returns:
            UserProfile | None: The user profile if found, otherwise None.
        """
        user = await UserRepository.get_user_by_username(username, db)
        if user:
            user.totp_secret_encrypted = seed
            user.is_totp_verified = True
            await db.commit()
            await db.refresh(user)
        return user
    
    @staticmethod
    async def update_user_email(username:str,email:str,db: AsyncSession)->UserProfile|None:
        """
        Update user totp.   
        Args:
            username (str): The username of the user to retrieve.
            email (str): New email address of the user
            db (AsyncSession): The database session.
        Returns:
            UserProfile | None: The user profile if found, otherwise None.
        """
        user = await UserRepository.get_user_by_username(username, db)
        if user:
            user.email_address=email
            user.is_email_address_verified = True
            await db.commit()
            await db.refresh(user)
        return user
    
    @staticmethod
    async def update_user_mobile(username:str,mobile:str,db: AsyncSession)->UserProfile|None:
        """
        Update user totp.   
        Args:
            username (str): The username of the user to retrieve.
            movile (str): New mobile number of the user
            db (AsyncSession): The database session.
        Returns:
            UserProfile | None: The user profile if found, otherwise None.
        """
        user = await UserRepository.get_user_by_username(username, db)
        if user:
            user.mobile_number=mobile
            user.is_mobile_number_verified = True
            await db.commit()
            await db.refresh(user)
        return user