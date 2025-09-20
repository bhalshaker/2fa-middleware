from pydantic import BaseModel

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