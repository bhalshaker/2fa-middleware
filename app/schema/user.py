from dataclasses import dataclass
from typing_extensions import Self
from typing import Optional
from pydantic import BaseModel,EmailStr,model_validator,constr
from pydantic import Field
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
    """Class to hold user profile information."""
    username:Optional[str]=None
    first_name:Optional[str]=None
    last_name:Optional[str]=None
    email:Optional[str]=None
    email_verified:Optional[bool]=None
    mobile:Optional[str]=None
    mobile_verified:Optional[bool]=None

class UserProfileInfoResponse(BaseModel):
    """Response model for user profile information."""
    successful:bool
    message:Optional[str]=None
    user_profile_info=Optional[UserProfileInfo]=None


class UpdateUserInfo(BaseModel):
    """Model to update user information"""

    email:Optional[EmailStr]=None
    mobile: Optional[constr] = Field(default=None, regex=r'^\+973\d{8}$')

    @model_validator(mode='after')
    def check_atleast_one_value(self)->Self:
        """Ensure at least one of email or mobile is provided."""

        if not self.email and not self.mobile:
            raise ValueError("At least one of 'email' or 'mobile' must be provided.")
        return self
class UpdateUserInfoResponse(BaseModel):
    successful:bool
    message:Optional[str]=""
    email_update_requested:Optional[bool]=False
    mobile_update_requested:Optional[bool]=False

@dataclass
class UpdateUserResults():
    successful_update:bool