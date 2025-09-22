from dataclasses import dataclass
import os

@dataclass(frozen=True)
class Settings:
    # OTP Settings
    issuer_name:str
    otp_size:int
    # Postgres Settings
    pg_db_user:str
    pg_db_password:str
    pg_db_database:str
    pg_db_host:str
    pg_db_port:int
    pg_db_pool_min_size:int
    pg_db_pool_max_size:int
    # Redis Settings
    redis_url:str
    redis_max_connections:int
    # Keycloak Settings
    keycloack_url:str
    keycloack_realm:str
    keycloack_client_id:str
    keycloack_client_secret:str
    keycloack_admin_username:str
    keycloack_admin_password:str

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
            keycloack_url=os.getenv("KEYCLOAK_URL","http://localhost:8080"),
            keycloack_realm=os.getenv("KEYCLOAK_REALM","master"),
            keycloack_client_id=os.getenv("KEYCLOAK_CLIENT_ID","admin-client"),
            keycloack_client_secret=os.getenv("KEYCLOAK_CLIENT_SECRET","secret"),
            keycloack_admin_username=os.getenv("KEYCLOAK_ADMIN_USERNAME","admin"),
            keycloack_admin_password=os.getenv("KEYCLOAK_ADMIN_PASSWORD","admin-password"),
        )

settings=Settings.from_env()