from app.config.settings import settings
import redis.asyncio as aioredis

class TOTPRepository():

    @staticmethod
    async def store_totp_seed(db:aioredis.Redis, username:str, seed:str):
        """
        Store the TOTP seed for a user.
        Args:
            db (aioredis.Redis): redis client instance
            username (str): username of the user want to store totp
            seed (str): totp seed to store
        """
        # Store TOTP with a key pattern: username:totp
        key = f"{username}:totp"
        await db.set(key, seed, ex=settings.redit_ttl)

    @staticmethod
    async def get_totp_seed(db:aioredis.Redis, username:str) -> str | None:
        """
        Get the TOTP seed for a user.
        Args:
            db (aioredis.Redis): redis client instance
            username (str): username of the user want to get totp
        Returns:
            str | None: The TOTP seed if found, else None.
        """
        key = f"{username}:totp"
        return await db.get(key)
    
    @staticmethod
    async def delete_totp_seed(db:aioredis.Redis, username:str):
        """
        Delete the TOTP seed for a user.
        Args:
            db (aioredis.Redis): redis client instance
            username (str): username of the user want to delete totp
        """
        key = f"{username}:totp"
        await db.delete(key)