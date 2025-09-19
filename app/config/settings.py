from dataclasses import dataclass
import os

@dataclass
class Settings:
    issuer_name:str
    otp_size:int
    pg_db_url:str
    pg_db_pool_size:int
    pg_db_max_overflow:int


    @staticmethod
    def from_env(cls):
        return cls(
            issuer_name=os.getenv("ISSUER_NAME","2FA-MIDDLEWARE"),
            otp_size=int(os.getenv("OTP_SIZE","6"))
        )