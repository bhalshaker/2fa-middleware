from dataclasses import dataclass
import os

@dataclass(frozen=True)
class Settings:
    # OTP Settings
    issuer_name:str
    otp_size:int
    otp_life:int
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
    redis_ttl:int
    # Keycloak Settings
    keycloak_url:str
    keycloak_realm:str
    keycloak_client_id:str
    keycloak_client_secret:str
    keycloak_admin_username:str
    keycloak_admin_password:str
    # Send Email Service API
    resend_from_email:str
    resend_api_url:str
    resend_api_key:str
    # Send SMS Service API
    twilio_account:str
    twilio_from_number:str
    twilio_auth_token:str

    @staticmethod
    def from_env():
        return Settings(
            issuer_name=os.getenv("ISSUER_NAME","2FA-MIDDLEWARE"),
            otp_size=int(os.getenv("OTP_SIZE","6")),
            otp_life=int(os.getenv("OTP_LIFE",10)),
            pg_db_user=os.getenv("PG_DB_USER","user"),
            pg_db_password=os.getenv("PG_DB_PASSWORD","password"),
            pg_db_database=os.getenv("PG_DB_DATABASE","6"),
            pg_db_host=os.getenv("PG_DB_HOST","6"),
            pg_db_port=int(os.getenv("PG_DB_PORT","6")),
            pg_db_pool_min_size=int(os.getenv("PG_DB_POOL_MIN_SIZE","6")),
            pg_db_pool_max_size=int(os.getenv("PG_DB_POOL_MAX_SIZE","6")),
            redis_url=os.getenv("REDIS_URL","redis://localhost:6379/0"),
            redis_max_connections=int(os.getenv("REDIS_MAX_CONNECTIONS","20")),
            redis_ttl=int(os.getenv("REDIS_TTL","660")),
            keycloak_url=os.getenv("KEYCLOAK_URL","http://localhost:8080"),
            keycloak_realm=os.getenv("KEYCLOAK_REALM","2faproject"),
            keycloak_client_id=os.getenv("KEYCLOAK_CLIENT_ID","fastapi-client"),
            keycloak_client_secret=os.getenv("KEYCLOAK_CLIENT_SECRET","secret"),
            keycloak_admin_username=os.getenv("KEYCLOAK_ADMIN_USERNAME","admin"),
            keycloak_admin_password=os.getenv("KEYCLOAK_ADMIN_PASSWORD","admin-password"),
            resend_from_email=os.getenv("RESEND_FROM_EMAIL","2FA-Middleware <onboarding@resend.dev>"),
            resend_api_url=os.getenv("RESEND_API_URL","https://api.resend.com/emails"),
            resend_api_key=os.getenv("RESEND_API_KEY",""),
            twilio_account=os.getenv("TWILIO_ACCOUNT",""),
            twilio_from_number=os.getenv("TWILIO_FROM_NUMBER",""),
            twilio_auth_token=os.getenv("TWILIO_AUTH_TOKEN","")
        )

settings=Settings.from_env()