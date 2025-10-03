from app.config.settings import settings
import httpx

class SMSHelper:

    @staticmethod
    def generate_sms_template(recepient_name,otp)->str:
        return f"""
            Hi {recepient_name}, your OTP is {otp}. It’s valid for {settings.otp_life} minutes. Keep it safe!
        """
    
    @staticmethod
    async def send_sms_otp(mobile,recepient_name,otp)->bool:
        try:
            send_sms_url=f"https://api.twilio.com/2010-04-01/Accounts/{settings.twilio_account}/Messages.json"
            data = {
                    "To": mobile,
                    "From": settings.twilio_from_number,
                    "Body":SMSHelper.generate_sms_template(recepient_name=recepient_name,otp=otp)
                }
            auth = (settings.twilio_account, settings.twilio_auth_token)  # Replace with your actual credentials
            async with httpx.AsyncClient() as client:
                response = await client.post(send_sms_url, data=data, auth=auth)
                response.raise_for_status()
                return True
        except Exception as exc:
            return False