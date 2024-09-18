# apis/utils.py
from datetime import datetime, timedelta

import jwt
from fastapi.security import OAuth2
from fastapi import Request, HTTPException
from typing import Optional
from starlette.status import HTTP_401_UNAUTHORIZED

from config import settings


class OAuth2PasswordBearerWithCookie(OAuth2):
    def __init__(self, tokenUrl: str, scheme_name: Optional[str] = None, scopes: Optional[dict] = None,
                 auto_error: bool = True):
        if not scopes:
            scopes = {}
        flows = {"password": {"tokenUrl": tokenUrl, "scopes": scopes}}
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        token = request.cookies.get("access_token")
        if not token:
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return token


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
