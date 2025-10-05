from fastapi import Depends,HTTPException,status
from app.helper.keycloak_helper import KeycloakHelper
from app.schema.token import TokenValidationResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import logging

security=HTTPBasic()
class AuthenticateUser():

    logger = logging.getLogger(__name__)

    @staticmethod
    async def get_logged_in_user(credentials: HTTPBasicCredentials = Depends(security))->TokenValidationResponse:
        token=await KeycloakHelper.generat_token(credentials.username,credentials.password)
        token_validation_results=await KeycloakHelper.validate_token(token.token)
        if not(token_validation_results.successful):
            AuthenticateUser.logger.info(f"Could not generate token for {credentials.username}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Token is Invalid or cannot be validated at the moment")
        AuthenticateUser.logger.info(f"Authentication results : {token_validation_results}")
        return token_validation_results
