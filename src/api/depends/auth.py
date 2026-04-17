from typing import Annotated

from fastapi import (
    Depends,
    Security,
)
from fastapi_jwt import JwtAuthorizationCredentials

from core.database import UnitOfWork

from core.security import access_security

from exceptions import (
    AuthenticationRequiredError,
    InvalidCredentialsError,
)

from models import User

from repositories import UserRepository

from services import AuthService

from .uow import get_uow
from .user import get_user_repository


def get_auth_service(
        uow: Annotated[
            UnitOfWork,
            Depends(get_uow),
        ]
) -> AuthService:
    return AuthService(uow=uow)


async def get_current_user(
        credentials: Annotated[
            JwtAuthorizationCredentials,
            Security(access_security),
        ],
        user_repository: Annotated[
            UserRepository,
            Depends(get_user_repository),
        ],
) -> User:
    if credentials is None:
        raise AuthenticationRequiredError()

    user_id = credentials.subject.get("user_id")
    if not user_id:
        raise AuthenticationRequiredError()

    user = await user_repository.get_by_id(obj_id=user_id)
    if not user or not user.is_active:
        raise AuthenticationRequiredError()

    return user


async def require_verified_user(
        credentials: Annotated[
            JwtAuthorizationCredentials,
            Security(access_security),
        ],
        user_repository: Annotated[
            UserRepository,
            Depends(get_user_repository),
        ],
) -> User:
    if credentials is None:
        raise AuthenticationRequiredError()

    if not credentials.subject.get("is_verified", False):
        raise InvalidCredentialsError()

    user_id = credentials.subject.get("user_id")
    if not user_id:
        raise AuthenticationRequiredError()

    user = await user_repository.get_by_id(obj_id=user_id)
    if not user or not user.is_active:
        raise AuthenticationRequiredError()

    return user