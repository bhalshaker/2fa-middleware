from typing import Annotated
from fastapi import Depends,HTTPException,status
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from app.helper.keycloak_helper import KeycloakHelper
from app.schema.token import TokenValidationResponse

http_bearer=HTTPBearer()

class AuthenticateUser():
    @staticmethod
    async def get_logged_in_user(token: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)])->TokenValidationResponse:
        token_validation_results=await KeycloakHelper.validate_token(token)
        if not(token_validation_results.successful):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                 detail="Token is Invalid or cannot be validated at the moment")
        return token_validation_results