from dataclasses import dataclass
import os

@dataclass(frozen=True)
class Settings:
    issuer_name:str
    otp_size:int
    pg_db_user:str
    pg_db_password:str
    pg_db_database:str
    pg_db_host:str
    pg_db_port:int
    pg_db_pool_min_size:int
    pg_db_pool_max_size:int


    @staticmethod
    def from_env():
        return Settings(
            issuer_name=os.getenv("ISSUER_NAME","2FA-MIDDLEWARE"),
            otp_size=int(os.getenv("OTP_SIZE","6")),
            pg_db_user=os.getenv("OTP_SIZE","6"),
            pg_db_password=os.getenv("OTP_SIZE","6"),
            pg_db_database=os.getenv("OTP_SIZE","6"),
            pg_db_host=os.getenv("OTP_SIZE","6"),
            pg_db_port=int(os.getenv("OTP_SIZE","6")),
            pg_db_pool_min_size=int(os.getenv("OTP_SIZE","6")),
            pg_db_pool_max_size=int(os.getenv("OTP_SIZE","6")),
        )

settings=Settings.from_env()