import string
import secrets

class OTPHelper:

    @staticmethod
    def generate_otp(otp_size:int=6):
        return ''.join(secrets.choice(string.digits) for _ in range(otp_size))