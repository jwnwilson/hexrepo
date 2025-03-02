from typing import Dict, Optional

import boto3
from app.config import config
from app.domain.user import UserPermissionCreateDTO, UserPermissionDTO
from loguru import logger

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
    UserUOW,
    UserVerifyDTO,
)


class CognitoAuthAdapter(AuthAdapter):
    # Need to ad UOW to add users and modify groups and permissions
    def __init__(self, uow: Optional[UserUOW] = None):
        if not config.CLIENT_ID or not config.JWT_SECRET:
            raise ValueError("Missing client_id or jwt_secret config values")
        self.client_id: str = config.CLIENT_ID
        self.jwn_secret: str = config.JWT_SECRET
        self.uow: Optional[UserUOW] = uow
        self._cognito_client: Optional[boto3.client] = None

    @property
    def cognito_client(self):
        if not self._cognito_client:
            self._cognito_client = boto3.client("cognito-idp", config.REGION)
        return self._cognito_client

    def login(self, user: UserLogin) -> str:
        try:
            response = self.cognito_client.initiate_auth(
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={"USERNAME": user.username, "PASSWORD": user.password},
                ClientId=self.client_id,
            )
            if "AuthenticationResult" not in response:
                raise UnathorizedException(response["ChallengeName"])
            logger.info(f"User {user.username} logged in")
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
            user_dto: UserPermissionDTO = self.uow.user.create(
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
            logger.info(f"Signed up user {user_dto.id}")
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
        
    def send_verification_code(self, username: str) -> None:
        logger.info(f"Sending verification code to {username}")
        self.cognito_client.resend_confirmation_code(
            ClientId=self.client_id, Username=username
        )

    def verify(self, user: UserVerifyDTO) -> None:
        try:
            self.cognito_client.confirm_sign_up(
                ClientId=self.client_id,
                Username=user.username,
                ConfirmationCode=user.confirmation_code,
            )
            logger.info(f"User {user.username} verified")
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
            logger.info(f"Removed User {user.username} from auth")
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            raise e
