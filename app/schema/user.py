from dataclasses import dataclass
from typing_extensions import Self
from typing import Optional
from pydantic import BaseModel,EmailStr,model_validator,constr
from uuid import uuid4

@dataclass
class KeycloakUserInfo():
    """Represents user information from Keycloak."""

    id:Optional[uuid4]=None
    username:Optional[str]=None
    first_name:Optional[str]=None
    last_name:Optional[str]=None
    email:Optional[str]=None
    email_verified:Optional[bool]=None
    mobile:Optional[str]=None
    mobile_verified:Optional[bool]=None

class UserProfileInfo(BaseModel):
    username:str
    first_name:str
    last_name:str
    email:str
    email_verified:Optional[bool]=None
    mobile:Optional[str]=None
    mobile_verified:Optional[bool]=None


class UpdateUserInfo(BaseModel):
    """Model to update user information"""

    username:str
    email:Optional[EmailStr]=None
    from pydantic import Field
    mobile: Optional[constr] = Field(default=None, regex=r'^\+973\d{8}$')

    @model_validator(mode='after')
    def check_atleast_one_value(self)->Self:
        """Ensure at least one of email or mobile is provided."""

        if not self.email and not self.mobile:
            raise ValueError("At least one of 'email' or 'mobile' must be provided.")
        return self

@dataclass
class UpdateUserResults():
    successful_update:bool