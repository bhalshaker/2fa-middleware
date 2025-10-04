from sqlalchemy.ext.asyncio import AsyncSession

class UserRepository():
    @staticmethod
    async def get_user_by_username(username:str,db: AsyncSession):
        pass

    @staticmethod
    async def update_user_totp(username:str,seed:str,db: AsyncSession):
        pass