import httpx
import logging
from app.config.settings import settings
from app.schema.token import TokenGenerationResponse,TokenValidationResponse
from app.schema.user import KeycloakUserInfo,UpdateUserInfo,UpdateUserResults
from app.exception.exceptions import TokenValidationError,TokenGenerationError,NoMatchingUserError

class KeycloakHelper:

    logger = logging.getLogger(__name__)

    @staticmethod
    def get_customized_attribute_value(attributes: dict, key: str):
        """Extracts a specific attribute value from a dictionary of attributes."""
        attribute_value = attributes.get(key, [""])
        return attribute_value[0] if isinstance(attribute_value, list) and attribute_value else None

    @staticmethod
    async def generat_token(username:str,password:str)->TokenGenerationResponse:
        """
        Generate user token.
        
        Args:
            username (str): Username.
            password (str): Password.

        Returns:
            token_response (TokenGenerationResponse): Returns the response of token generation request.
        """
        # Generate Token generation URL
        token_url = f"{settings.keycloak_url}/realms/{settings.keycloak_realm}/protocol/openid-connect/token"
        # Generate request body payload
        payload = {
                 "grant_type": "password",
                 "username": username,
                 "password": password,
                 "client_id": settings.keycloak_client_id,
                 "client_secret": settings.keycloak_client_secret,
            }
        # Define request header
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        async with httpx.AsyncClient() as client:
            try:
                # Call Keyclock RestAPI to generate the token
                response = await client.post(token_url, data=payload, headers=headers)
                # If request failed raise an error
                response.raise_for_status()
                # Load response into token_data
                token_data = response.json()
                # Return Token (map to TokenGenerationResponse dataclass fields)
                return TokenGenerationResponse(
                    successful=True,
                    token=token_data.get("access_token"),
                    token_type=token_data.get("token_type"),
                    token_expires_in=token_data.get("expires_in", 0),
                )
            except Exception as exc:
                # Catch all possible errors such as network failure and invalid credentials
                KeycloakHelper.logger.exception("Error generating token for user %s", username)
                return TokenGenerationResponse(successful=False, token=None, token_type=None, token_expires_in=0)


    @staticmethod
    async def get_admin_token()->TokenGenerationResponse:
        """Fetches an admin token from Keycloak using admin user credentials."""
        # use admin password from settings
        return await KeycloakHelper.generat_token(settings.keycloak_admin_username, settings.keycloak_admin_password)
    
    @staticmethod
    async def validate_token(token: str)->TokenValidationResponse:
        # Generate Token validation URL
        token_url = f"{settings.keycloak_url}/realms/{settings.keycloak_realm}/protocol/openid-connect/token/introspect"
        # Define request header
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        # Generate request body payload
        payload = {
        "client_id": settings.keycloak_client_id,
        "client_secret": settings.keycloak_client_secret,
        "token": token
        }
        KeycloakHelper.logger.info(f"# Token Validation Payload:{payload}")
        async with httpx.AsyncClient() as client:
            try:
                # Call Keyclock RestAPI to validate the token
                response = await client.post(token_url, data=payload, headers=headers)
                KeycloakHelper.logger.info("introspect status=%s", response.status_code)
                KeycloakHelper.logger.info("introspect body=%s", response.text)  # safe for debugging; avoid tokens in prod logs
                # If request failed raise an error
                response.raise_for_status()
                # Load response into validation_data (introspection response)
                validation_data = response.json()
                # If token is not active, raise a validation error
                KeycloakHelper.logger.info(validation_data)
                if not validation_data.get("active", False):
                    raise TokenValidationError()
                # Return username mapped to TokenValidationResponse dataclass
                return TokenValidationResponse(
                    successful=True,
                    username=validation_data.get("preferred_username")
                )
            except Exception as exc:
                # Catch all possible errors such as network failure and invalid token
                KeycloakHelper.logger.exception("Error validating token")
                return TokenValidationResponse(successful=False, username=None)
    
    # Get a Matching username
    async def return_matching_user_info(username:str)->KeycloakUserInfo:
        """
        Look for a matching user in keyclock and return the user info

        Args:
            username (str): username to search for

        Returns:
            KeycloakUserInfo: Matching username info
        """
        matching_user_info=None
        try:
            # Generate Admin token
            admin_token=await KeycloakHelper.get_admin_token()
            # Raise an error if Admin token cannot be generated
            if not(admin_token.successful):
                raise TokenGenerationError()
            # Generate Token validation URL
            search_user_url = f"{settings.keycloak_url}/admin/realms/{settings.keycloak_realm}/users?username={username}"
            # Define request header
            headers = {"Authorization": f"Bearer {admin_token.token}"}
            async with httpx.AsyncClient() as client:
                response=await client.get(url=search_user_url,headers=headers)
                response.raise_for_status()
                search_results=response.json()
                if len(search_results)==0:
                    pass # Return no matching user was found
                # Find matching user
                for user in search_results:
                    if user.get("username") == username:
                        matching_user_info=user
                # If no matching user was found raise an Error
                if matching_user_info==None:
                    raise NoMatchingUserError()
            # Return Matching username info
            mobile_verified=True if str(KeycloakHelper.get_customized_attribute_value(matching_user_info.get("attributes",{}),"mobileVerified")).lower == "true" else False
            return KeycloakUserInfo(id=matching_user_info.get("id"),
                                    username=matching_user_info.get("username"),
                                    first_name=matching_user_info.get("firstName"),
                                    last_name=matching_user_info.get("lastName"),
                                    email=matching_user_info.get("email"),
                                    email_verified=matching_user_info.get("emailVerified"),
                                    mobile=KeycloakHelper.get_customized_attribute_value(matching_user_info.get("attributes",{}),"mobile"),
                                    mobile_verified=mobile_verified
                                    )
            
        except Exception as exc:
            # Log and return Empty KeycloakUserInfo in case of a failure or non matching user.
            KeycloakHelper.logger.exception("Error retrieving matching user info for username=%s", username)
            return KeycloakUserInfo()

    async def update_user_attributes(userinfo:UpdateUserInfo)->UpdateUserResults:
        try:
            # Get Matching User info and if there is no match raise an Error
            retrieved_user_info=await KeycloakHelper.return_matching_user_info(userinfo.username)
            if retrieved_user_info.id == None:
                raise NoMatchingUserError()
            mobile=[retrieved_user_info.mobile] if retrieved_user_info.mobile else []
            mobile_verified=["true"] if retrieved_user_info.mobile_verified else ["false"]
            # Update payload
            payload={
                        "firstName": retrieved_user_info.first_name,
                        "lastName": retrieved_user_info.last_name,
                        "email": userinfo.email if userinfo.email else retrieved_user_info.email,
                        "emailVerified": True if userinfo.email else retrieved_user_info.email_verified,
                        "attributes": {
                            "mobile": [userinfo.mobile] if userinfo.mobile else mobile,
                            "mobileVerified":["true"] if userinfo.mobile else mobile_verified
                        }
                    }
            # Generate Admin token
            admin_token=await KeycloakHelper.get_admin_token()
            # Raise an error if Admin token cannot be generated
            if not(admin_token.successful):
                raise TokenGenerationError
            # Generate user update url
            generate_user_update_url = f"{settings.keycloak_url}/admin/realms/{settings.keycloak_realm}/users/{retrieved_user_info.id}"
            headers={'Content-Type': 'application/json',
                     "Authorization": f"Bearer {admin_token.token}"}
            async with httpx.AsyncClient() as client:
                update_user_info_response=await client.put(url=generate_user_update_url,data=payload,headers=headers)
                update_user_info_response.raise_for_status()
                return UpdateUserResults(True)
        except Exception as exc:
            KeycloakHelper.logger.exception("Error updating user attributes for username=%s", getattr(userinfo, "username", None))
            return UpdateUserResults(False)