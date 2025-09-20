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
    redis_url:str
    redis_max_connections:int

    @staticmethod
    def from_env():
        return Settings(
            issuer_name=os.getenv("ISSUER_NAME","2FA-MIDDLEWARE"),
            otp_size=int(os.getenv("OTP_SIZE","6")),
            pg_db_user=os.getenv("PG_DB_USER","user"),
            pg_db_password=os.getenv("PG_DB_PASSWORD","password"),
            pg_db_database=os.getenv("PG_DB_DATABASE","6"),
            pg_db_host=os.getenv("PG_DB_HOST","6"),
            pg_db_port=int(os.getenv("PG_DB_PORT","6")),
            pg_db_pool_min_size=int(os.getenv("PG_DB_POOL_MIN_SIZE","6")),
            pg_db_pool_max_size=int(os.getenv("PG_DB_POOL_MAX_SIZE","6")),
            redis_url=os.getenv("REDIS_URL","redis://localhost:6379/0"),
            redis_max_connections=int(os.getenv("REDIS_MAX_CONNECTIONS","20")),
        )

settings=Settings.from_env()