from typing import Dict, List, Optional

import requests
from fastapi import HTTPException
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwk, jwt
from jose.utils import base64url_decode
from loguru import logger
from pydantic import BaseModel
from starlette.requests import Request
from starlette.status import HTTP_403_FORBIDDEN
from hexrepo_cloud.auth.interface import FastapiJWTMiddleware, JWTAuthorizationCredentials

from app.config import config


JWK = Dict[str, str]


class JWKS(BaseModel):
    keys: List[JWK]


class FastapiJWTCognitoMiddleware(FastapiJWTMiddleware, HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)
        keys_url = (
            "https://cognito-idp.{}.amazonaws.com/{}/.well-known/jwks.json".format(
                config.REGION, config.USER_POOL_ID
            )
        )
        try:
            self.jwks: JWKS = JWKS.model_validate(requests.get(keys_url).json())
        except requests.RequestException:
            logger.exception("Error fetching JWKs")
            raise
        self.kid_to_jwk = {jwk["kid"]: jwk for jwk in self.jwks.keys}

    def verify_jwk_credentials(self, jwt_credentials: JWTAuthorizationCredentials) -> bool:
        try:
            public_key = self.kid_to_jwk[jwt_credentials.header["kid"]]
        except KeyError:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail="JWK public key not found"
            )

        key = jwk.construct(public_key)
        decoded_signature = base64url_decode(jwt_credentials.signature.encode())

        return key.verify(jwt_credentials.message.encode(), decoded_signature)

    def verify_jwt_token(self, jwt_token: str) -> JWTAuthorizationCredentials:
        try:
            message, signature = jwt_token.rsplit(".", 1)
        except ValueError:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail="JWT token invalid"
            )

        try:
            jwt_credentials = JWTAuthorizationCredentials(
                jwt_token=jwt_token,
                header=jwt.get_unverified_header(jwt_token),
                claims=jwt.get_unverified_claims(jwt_token),
                signature=signature,
                message=message,
            )
        except JWTError:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail="JWK invalid"
            )

        if not self.verify_jwk_credentials(jwt_credentials):
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail="JWK invalid"
            )

        return jwt_credentials

    async def __call__(self, request: Request) -> Optional[JWTAuthorizationCredentials]:
        authorization: Optional[str] = request.headers.get("Authorization") or request.session.get("token")
        scheme, credentials = get_authorization_scheme_param(authorization)
        if not (authorization and scheme and credentials):
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN, detail="Not authenticated"
                )
            else:
                return None
        if scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail="Invalid authentication credentials",
                )
            else:
                return None
        credentials = HTTPAuthorizationCredentials(scheme=scheme, credentials=credentials)

        if credentials:
            jwt_token = credentials.credentials
            return self.verify_jwt_token(jwt_token)
        
        return None


get_jwt_token: FastapiJWTMiddleware = FastapiJWTCognitoMiddleware()
