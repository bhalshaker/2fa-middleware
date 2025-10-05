from pydantic import BaseModel
from typing import Optional

class SeedURIImage(BaseModel):
    """Class to hold TOTP seed URI and QR code image."""
    seed_uri: str
    qrcode: str

class SeedFullInfo(BaseModel):
    """Class to hold full TOTP information including seed, username, seed URI, and QR code image."""
    seed: str
    user_name:str
    seed_uri: str
    qrcode: str

class TOTPGenerationResult(BaseModel):
    """Class to hold TOTP generation result."""
    successful: bool
    message: Optional[str] = None
    data: Optional[SeedFullInfo] = None

class TOTPVerificationResult(BaseModel):
    """Class to hold TOTP verification result."""
    successful: bool
    message: Optional[str] = None

class SendTOTP(BaseModel):
    totp:str
    is_new_seed:Optional[bool]=False