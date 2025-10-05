import httpx
from app.config.settings import settings
import logging

class EmailHelper:
  logger=logging.getLogger(__name__)
  @staticmethod
  def generate_otp_email_template(recepient_name:str,otp:str):
    return f"""<!DOCTYPE html>
        <html>
<head>
  <meta charset="UTF-8">
  <title>OTP Code for Email Validation</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      background-color: #f4f4f4;
      margin: 0;
      padding: 0;
    }}
    .email-container {{
      max-width: 600px;
      margin: 40px auto;
      background-color: #ffffff;
      padding: 30px;
      border-radius: 8px;
      box-shadow: 0 0 10px rgba(0,0,0,0.1);
    }}
    .header {{
      text-align: center;
      padding-bottom: 20px;
    }}
    .otp-code {{
      font-size: 24px;
      font-weight: bold;
      color: #2c3e50;
      text-align: center;
      margin: 20px 0;
    }}
    .message {{
      font-size: 16px;
      color: #333333;
      line-height: 1.6;
    }}
    .footer {{
      font-size: 14px;
      color: #888888;
      text-align: center;
      margin-top: 30px;
    }}
  </style>
</head>
<body>
  <div class="email-container">
    <div class="header">
      <h2>Your One-Time Password (OTP) to verify your email</h2>
    </div>
    <div class="message">
      <p>Dear {recepient_name},</p>
      <p>FastAPI 2FA-Middleware initiated a request to verify your email. Please use the OTP below to proceed with Email confirmation process:</p>
    </div>
    <div class="otp-code">
      {otp}
    </div>
    <div class="message">
      <p>This code is valid for the next <strong>{settings.otp_life} minutes</strong>. Please do not share this code with anyone.</p>
      <p>Follow http://localhost:8080/docs documentaion to enter your OTP</p>
      <p>If you did not request this, please ignore this email.</p>
    </div>
    <div class="footer">
      <p>Thank you,<br>
      2FA-Middleware Team<br></p>
    </div>
  </div>
</body>
</html>
"""
  # @staticmethod
  # def generate_otp_email_template(recepient_name,otp):s
  #   return f"Hello <strong>{recepient_name}</strong> Please enter your OTP code : <strong>{otp}</strong> in {settings.otp_life} minutes"
  @staticmethod
  async def send_email_otp(email:str,recepient_name:str,otp:str):
    html= EmailHelper.generate_otp_email_template(recepient_name,otp)
    headers={
             "Authorization": f"Bearer {settings.resend_api_key}"
    }
    payload={
                "from": settings.resend_from_email,
                "to": [email],
                "subject": '2FA Middleware Email OTP',
                "html":html
    }
    EmailHelper.logger.info(f"Resend payload:{payload}")
    async with httpx.AsyncClient() as client:
      response = await client.post(url=settings.resend_api_url, json=payload, headers=headers)
      if response.status_code >= 400:
        # print full body to understand the 4xx/5xx reason from Resend
        EmailHelper.logger.error(f"Resend API error: {response.status_code}")
        try:
          EmailHelper.logger.error(f"response.json(): {response.json()}")
        except Exception:
          EmailHelper.logger.error(f"response.text(): {response.text}")
      response.raise_for_status()
