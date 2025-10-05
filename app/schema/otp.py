from pydantic import BaseModel,field_validator
from typing import Optional

class SendOTPSchema(BaseModel):
    otp:str
    otp_type: str

    @field_validator('otp_type')
    def validate_otp_type(cls, v):
        v = v.lower()
        if v not in ['mobile', 'email']:
            raise ValueError('otp_type must be either "mobile" or "email"')
        return v
    
class OTPVerificationResponse(BaseModel):
    successful: bool
    message: Optional[str] = None