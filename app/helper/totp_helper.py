import pyotp
from app.config.settings import Settings
class TOTPHelper():


    @staticmethod
    def generate_seed():
        return pyotp.random_base32()

    @staticmethod
    def genererate_seed_uri(seed:str,name:str)->str:
        #Get Issuer name from settings
        totp=pyotp.TOTP(seed)
        return totp.provisioning_uri(name=name,issuer_name=issuer_name)

    
    @staticmethod
    def verify_totp(seed:str,totp_code)->bool:
        totp=pyotp.TOTP(seed)
        return totp.now()==totp_code