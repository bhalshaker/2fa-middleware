from dataclasses import dataclass

@dataclass
class TokenGenerationResponse:
    """
        Holds the value of Token Response
    """
    successful:bool
    token:str
    token_type:str
    token_expires_in:int


@dataclass
class TokenValidationResponse:
    """
        Returns the username if the token is valid
    """
    successful:bool
    username:str

