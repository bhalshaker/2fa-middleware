import httpx
from app.config.settings import settings
from app.schema.token import TokenGenerationResponse,TokenValidationResponse
from app.schema.user import KeycloakUserInfo,UpdateUserInfo,UpdateUserResults
from app.exception.exceptions import TokenValidationError,TokenGenerationError,NoMatchingUserError

class KeycloakHelper:

    @staticmethod
    def get_customized_attribute_value(attributes: dict, key: str):
        """Extracts a specific attribute value from a dictionary of attributes."""
        attribute_value = attributes.get(key, [])
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
        token_url = f"{settings.keycloack_url}/realms/{settings.keycloack_realm}/protocol/openid-connect/token"
        # Generate request body payload
        payload = {
                 "grant_type": "password",
                 "username": username,
                 "password": password,
                 "client_id": settings.keycloack_client_id,
                 "client_secret": settings.keycloack_client_secret,
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
                # Return Token
                return TokenGenerationResponse(
                    success=True,
                    access_token=token_data.get("access_token"),
                    token_type=token_data.get("token_type"),
                    expires_in=token_data.get("expires_in", 0),
                )
            except Exception as exc:
            # Catch all possible of errors such as network failure and invalid cerdintials
                return TokenGenerationResponse(success=False, access_token=None, token_type=None, expires_in=0)


    @staticmethod
    async def get_admin_token()->TokenGenerationResponse:
        """Fetches an admin token from Keycloak using admin user credentials."""
        return await KeycloakHelper.generat_token(settings.keycloack_admin_username,settings.keycloack_admin_username)
    
    @staticmethod
    async def validate_token(token: str)->TokenValidationResponse:
        # Generate Token validation URL
        token_url = f"{settings.keycloack_url}/realms/{settings.keycloack_realm}/protocol/openid-connect/token/introspect"
        # Generate request body payload
        payload = {
                 "client_id": settings.keycloack_client_id,
                 "client_secret": settings.keycloack_client_secret,
                 "token":token,
            }
        # Define request header
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        async with httpx.AsyncClient() as client:
            try:
                # Call Keyclock RestAPI to validate the token
                response = await client.post(token_url, data=payload, headers=headers)
                # If request failed raise an error
                response.raise_for_status()
                # Load response into token_data
                validation_data = response.json()
                if validation_data.get("active")==False:
                    raise TokenValidationError()
                # Return username
                return TokenValidationResponse(
                    success=True,
                    username=validation_data.get("preferred_username")
                )
            except Exception as exc:
            # Catch all possible of errors such as network failure and invalid token
                return TokenValidationResponse(success=False, username=None)
    
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
            search_user_url = f"{settings.keycloack_url}/admin/realms/{settings.keycloack_realm}/users?username={username}"
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
            return KeycloakUserInfo(id=matching_user_info.get("id"),
                                    username=matching_user_info.get("username"),
                                    first_name=matching_user_info.get("firstName"),
                                    last_name=matching_user_info.get("lastName"),
                                    email=matching_user_info.get("email"),
                                    email_verified=matching_user_info.get("emailVerified"),
                                    mobile=KeycloakHelper.get_customized_attribute_value(matching_user_info.get("attributes",{}),"mobile"),
                                    mobile_verified=KeycloakHelper.get_customized_attribute_value(matching_user_info.get("attributes",{}),"mobileVerified"),
                                    )
            
        except Exception as exc:
            # Return Empty KeycloakUserInfo in case of a failure or non matching user.
            return KeycloakUserInfo()

    async def update_user_attributes(userinfo:UpdateUserInfo)->UpdateUserResults:
        try:
            # Get Matching User info and if there is no match raise an Error
            retrieved_user_info=await KeycloakHelper.return_matching_user_info(userinfo.username)
            if retrieved_user_info.id == None:
                raise NoMatchingUserError()
            mobile=[retrieved_user_info.mobile] if retrieved_user_info.mobile else []
            mobile_verified=[retrieved_user_info.mobile_verified] if retrieved_user_info.mobile_verified else []
            # Update payload
            payload={
                        "firstName": retrieved_user_info.first_name,
                        "lastName": retrieved_user_info.last_name,
                        "email": userinfo.email if userinfo.email else retrieved_user_info.email,
                        "emailVerified": True if userinfo.email else retrieved_user_info.email_verified,
                        "attributes": {
                            "mobile": [userinfo.mobile] if userinfo.mobile else mobile,
                            "mobileVerified":[True if userinfo.mobile else mobile_verified]
                        }
                    }
            # Generate Admin token
            admin_token=await KeycloakHelper.get_admin_token()
            # Raise an error if Admin token cannot be generated
            if not(admin_token.successful):
                raise TokenGenerationError
            # Generate user update url
            generate_user_update_url = f"{settings.keycloack_url}/admin/realms/{settings.keycloack_realm}/users/{retrieved_user_info.id}"
            headers={'Content-Type': 'application/json',
                     "Authorization": f"Bearer {admin_token.token}"}
            async with httpx.AsyncClient() as client:
                update_user_info_response=await client.put(url=generate_user_update_url,data=payload,headers=headers)
                update_user_info_response.raise_for_status()
                return UpdateUserResults(True)
        except Exception as exc:
            return UpdateUserResults(False)