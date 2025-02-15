from typing import Dict, Optional

from app.domain.user import UserPermissionCreateDTO, UserPermissionDTO
import boto3
from loguru import logger

from app.config import config

from ..exceptions import (
    InvalidPasswordException,
    InvalidVerificationCodeException,
    UnathorizedException,
    UserExistsException,
)
from ..interface import (
    AuthAdapter,
    SignupResponse,
    UserDTO,
    UserLogin,
    UserSignupDTO,
    UserVerifyDTO,
    UserUOW
)


class CognitoAuthAdapter(AuthAdapter):
    # Need to ad UOW to add users and modify groups and permissions
    def __init__(self, uow: Optional[UserUOW] = None):
        self.client_id: str = config.CLIENT_ID
        self.jwn_secret: str = config.JWT_SECRET
        self.cognito_client = boto3.client("cognito-idp", config.REGION)
        self.uow: Optional[UserUOW] = uow

    def login(self, user: UserLogin) -> str:
        try:
            response = self.cognito_client.initiate_auth(
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={"USERNAME": user.username, "PASSWORD": user.password},
                ClientId=self.client_id,
            )
            if "AuthenticationResult" not in response:
                raise UnathorizedException(response["ChallengeName"])
            return response["AuthenticationResult"]["AccessToken"]
        except self.cognito_client.exceptions.NotAuthorizedException:
            raise UnathorizedException
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            raise e

    def logout(self, token: str) -> Dict:
        try:
            response = self.cognito_client.global_sign_out(AccessToken=token)
            return response
        except Exception as e:
            logger.error(f"Error logging out user: {e}")
            raise e

    def register(self, user: UserSignupDTO) -> SignupResponse:
        assert self.uow, "Miss configured auth, unable to register user"
        try:
            response: Dict = self.cognito_client.sign_up(
                ClientId=self.client_id,
                Username=user.username,
                Password=user.password,
                UserAttributes=[
                    {"Name": "email", "Value": user.email},
                    {"Name": "name", "Value": user.name},
                ],
            )
            self.uow.user.create(
                UserPermissionCreateDTO(
                    username=user.username,
                    email=user.email,
                    name=user.name,
                    permissions=[],
                    groups=[],
                    cognito_id=response["UserSub"],
                    verified=response["UserConfirmed"],
                    company=None,
                )
            )
            return SignupResponse(
                verified=response["UserConfirmed"],
                verification_code_destination=response["CodeDeliveryDetails"][
                    "DeliveryMedium"
                ],
            )
        except self.cognito_client.exceptions.InvalidPasswordException as err:
            raise InvalidPasswordException(err)
        except self.cognito_client.exceptions.UsernameExistsException as err:
            raise UserExistsException(err)
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            raise e

    def verify(self, user: UserVerifyDTO) -> None:
        try:
            self.cognito_client.confirm_sign_up(
                ClientId=self.client_id,
                Username=user.username,
                ConfirmationCode=user.confirmation_code,
            )
            # Add user to user group
            return
        except self.cognito_client.exceptions.CodeMismatchException as err:
            raise InvalidVerificationCodeException(err)
        except Exception as e:
            logger.error(f"Error verifying user: {e}")
            raise e
        
    def delete_user(self, user: UserDTO) -> None:
        try:
            self.cognito_client.admin_delete_user(
                UserPoolId=config.USER_POOL_ID,
                Username=user.username,
            )
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            raise e
