from typing import Dict
import boto3
from loguru import logger
from app.config import config

from projects.auth.src.app.adaptor.auth.exceptions import UserExistsException, UnathorizedException
from .interface import AuthAdapter, UserDTO


class CognitoAuthAdapter(AuthAdapter):
    def __init__(self):
        self.client_id: str = config.CLIENT_ID
        self.jwn_secret: str = config.JWT_SECRET
        self.cognito_client = boto3.client('cognito-idp', config.REGION)

    def login(self, username: str, password: str) -> str:
        try:
            response = self.cognito_client.initiate_auth(
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': username,
                    'PASSWORD': password
                },
                ClientId=self.client_id
            )
            return response['AuthenticationResult']['AccessToken']
        except self.cognito_client.exceptions.NotAuthorizedException:
            raise UnathorizedException
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            raise e
        
    def logout(self, token: str) -> Dict:
        try:
            response = self.cognito_client.global_sign_out(
                AccessToken=token
            )
            return response
        except Exception as e:
            logger.error(f"Error logging out user: {e}")
            raise e

    def register(self, user: UserDTO) -> Dict:
        try:
            response = self.cognito_client.sign_up(
                ClientId=self.client_id,
                username=user.username,
                password=user.password,
                UserAttributes=[
                    {
                        'Name': 'email',
                        'Value': user.email
                    }
                ]
            )
            return response
        except self.cognito_client.exceptions.UsernameExistsException:
            raise UserExistsException
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            raise e

    def verify(self, user: UserDTO) -> Dict:
        try:
            response = self.cognito_client.confirm_sign_up(
                ClientId=self.client_id,
                Username=user.username,
                ConfirmationCode=user.confirmation_code
            )
            return response
        except Exception as e:
            logger.error(f"Error verifying user: {e}")
            raise e