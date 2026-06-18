from datetime import datetime, timedelta, timezone
from typing import Any
from fastapi import Request
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
import jwt
import bcrypt
from settings import settings
from enum import Enum
from sqlmodel import SQLModel


class TokenType(Enum):
    access_token = "access_token"
    refresh_token = "refresh_token"
    verify_token = "verify_token"
    activate_token = "activate_token"
    reset_token = "reset_token"


class TokenPayload(SQLModel):
    sub: str | None = None


ALGORITHM = "HS256"


def create_token(subject: str | Any, expires_delta: timedelta, type: str) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    payload = {"exp": expire, "sub": str(subject), "type": type}
    encoded_jwt = jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str | None) -> bool:
    if not hashed_password:
        return False
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


class OAuth2WithCookie(OAuth2):
    def __init__(self, *args, cookie_name: str = "access_token", **kwargs):
        super().__init__(*args)
        self.cookie_name = cookie_name

    def __call__(self, request: Request) -> str | None:
        authorization: str | None = request.cookies.get(self.cookie_name)
        if authorization:
            return authorization
        else:
            return None
