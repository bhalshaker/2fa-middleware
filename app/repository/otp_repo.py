from app.config.settings import settings
import redis.asyncio as aioredis

class OTPRepository():
    @staticmethod
    async def store_email_otp(db:aioredis.Redis, username:str, email:str, otp:str):
        """
        Store the email OTP for a user.

        Args:
            db (aioredis.Redis): redis client instance
            username (str): username of the user want to store otp
            email (str): email of the user want to store otp
            otp (str): otp code to store
        """
        # Store OTP with a key pattern: username:email:<email>
        key = f"{username}:email:{email}"
        await db.set(key, otp, ex=settings.redis_ttl)
    
    @staticmethod
    async def store_sms_otp(db:aioredis.Redis, username:str, mobile:str, otp:str):
        """
        Store the mobile OTP for a user.
        Args:
            db (aioredis.Redis): redis client instance
            username (str): username of the user want to store otp
            mobile (str): mobile number of the user want to store otp
            otp (str): otp code to store
        """
        # Store OTP with a key pattern: username:mobile:<mobile>
        key = f"{username}:mobile:{mobile}"
        await db.set(key, otp, ex=settings.redis_ttl)

    @staticmethod
    async def find_user_key_value_by_otp(db: aioredis.Redis, username: str, otp: str,otp_type:str) -> str | None:
        """
        Find the identifier (email or mobile) associated with the given OTP for a user.
        Args:
            db (aioredis.Redis): redis client instance
            username (str): username of the user want to find otp
            otp (str): otp code to search
            otp_type (str): type of otp to search ("email" or "mobile")
        Returns:
            str | None: The identifier (email or mobile) if found, else None.
        """
        identifier_value = None
        try:
            # Validate OTP type
            if otp_type not in ["mobile","email"]:
                raise ValueError("Invalid OTP type")
            # Construct the key pattern to search
            pattern = f"{username}:{otp_type}:*"
            # Scan through keys matching the pattern
            keys = await db.keys(pattern)
            # Iterate through the keys to find the matching OTP
            for key in keys:
                value = await db.get(key)
                if value == otp:
                    # Extract the identifier from the key: username:otp_type:<identifier>
                    identifier_value = key.split(":", 2)[-1]
                return identifier_value
            return identifier_value
        except Exception as exc:
            return identifier_value
        
    @staticmethod
    async def confirm_and_delete_otp(db: aioredis.Redis, username:str, identifier:str, otp:str, otp_type:str)->bool:
        """
        Confirm the OTP for a user and delete it if it matches.
        Args:
            db (aioredis.Redis): redis client instance
            username (str): username of the user want to confirm otp
            identifier (str): email or mobile number associated with the OTP
            otp (str): otp code to confirm
            otp_type (str): type of otp to confirm ("email" or "mobile")
        Returns:
            bool: True if OTP is confirmed and deleted, False otherwise.
        """
        try:
            # Validate OTP type
            if otp_type not in ["mobile","email"]:
                raise ValueError("Invalid OTP type")
            # Construct the key pattern to search
            pattern = f"{username}:{otp_type}:{identifier}"
            # Retrieve the stored OTP
            stored_otp = await db.get(pattern)
            if not stored_otp:
                return False  # No OTP found
            # Compare and delete if it matches
            if stored_otp == otp:
                await db.delete(pattern)
                return True  # OTP confirmed and deleted
            return False  # OTP mismatch
        except Exception as exc:
            return False
