from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Request,
    Response,
    Security,
)
from fastapi_jwt import JwtAuthorizationCredentials
from starlette import status

from core.security import access_security

from api.depends import (
    get_auth_service,
    get_current_user,
)

from models import User

from schemas import (
    RegisterRequest,
    RegisterResponse,
    AccessTokenResponse,
    OtpCodeRequest,
    OtpCodeResponse,
    AccessRefreshTokens,
    LoginRequest,
    LoginResponse,
)

from exceptions import InvalidRefreshTokenError

from services import AuthService

from core.config import settings


router = APIRouter(
    prefix=settings.api.v1.auth,
    tags=["Auth"],
)


def _set_auth_cookies(response: Response, tokens: AccessRefreshTokens) -> None:
    response.set_cookie(
        key=settings.jwt.access_token_cookie_key,
        value=tokens.access_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=settings.jwt.access_token_expires,
    )
    response.set_cookie(
        key=settings.jwt.refresh_token_cookie_key,
        value=tokens.refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=settings.jwt.refresh_token_expires * 86400,
        path="/api/v1/auth/refresh",
    )


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(key=settings.jwt.access_token_cookie_key)
    response.delete_cookie(
        key=settings.jwt.refresh_token_cookie_key,
        path="/api/v1/auth/refresh",
    )


@router.post(
    path="/registration",
    summary="Зарегистрировать нового пользователя",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def registration(
        request: Request,
        response: Response,
        service: Annotated[
            AuthService,
            Depends(get_auth_service)
        ],
        schema: RegisterRequest,
):
    user_agent = request.headers.get("User-Agent")
    result = await service.registration(
        schema=schema,
        header=user_agent,
    )
    _set_auth_cookies(
        response=response,
        tokens=result,
    )
    return RegisterResponse(
        message=(
            f"Вы успешно зарегистрировались! "
            f"На почту был отправлен код подтверждения. "
            "Пожалуйста, введите его для завершения регистрации."
        ),
        token=AccessTokenResponse(
            access_token=result.access_token,
        ),
    )


@router.post(
    path="/confirm-registration",
    summary="Подтвердить регистрацию",
    response_model=OtpCodeResponse,
    status_code=status.HTTP_200_OK,
)
async def confirm_registration(
        response: Response,
        credentials: Annotated[
            JwtAuthorizationCredentials,
            Security(access_security),
        ],
        user: Annotated[
            User,
            Depends(get_current_user),
        ],
        service: Annotated[
            AuthService,
            Depends(get_auth_service),
        ],
        schema: OtpCodeRequest,
):
    session_uid = credentials.subject.get("session_uid")
    result = await service.confirm_registration(
        user_id=user.id,
        session_uid=session_uid,
        schema=schema,
    )
    _set_auth_cookies(
        response=response,
        tokens=result,
    )
    return OtpCodeResponse(
        message="Регистрация подтверждена!",
        token=AccessTokenResponse(
            access_token=result.access_token,
        ),
    )


@router.post(
    path="/login",
    summary="Войти в систему",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
)
async def login(
        request: Request,
        response: Response,
        service: Annotated[
            AuthService,
            Depends(get_auth_service),
        ],
        schema: LoginRequest,
):
    user_agent = request.headers.get("User-Agent")
    result = await service.login(
        schema=schema,
        header=user_agent,
    )
    _set_auth_cookies(
        response=response,
        tokens=result,
    )
    return LoginResponse(
        message="Вы успешно вошли в систему!",
        token=AccessTokenResponse(
            access_token=result.access_token,
        ),
    )


@router.post(
    path="/logout",
    summary="Выйти из системы",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(
        request: Request,
        response: Response,
        service: Annotated[
            AuthService,
            Depends(get_auth_service),
        ],
):
    plain_refresh_token = request.cookies.get(settings.jwt.refresh_token_cookie_key)
    if not plain_refresh_token:
        raise InvalidRefreshTokenError()

    await service.logout(plain_refresh_token=plain_refresh_token)
    _clear_auth_cookies(response=response)


@router.post(
    path="/refresh",
    summary="Обновить токены (ротация refresh-токена)",
    response_model=AccessTokenResponse,
    status_code=status.HTTP_200_OK,
)
async def refresh(
        request: Request,
        response: Response,
        service: Annotated[
            AuthService,
            Depends(get_auth_service)
        ],
):
    plain_refresh_token = request.cookies.get(settings.jwt.refresh_token_cookie_key)
    if not plain_refresh_token:
        raise InvalidRefreshTokenError()

    result = await service.refresh_tokens(plain_refresh_token=plain_refresh_token)
    _set_auth_cookies(
        response=response,
        tokens=result,
    )
    return AccessTokenResponse(access_token=result.access_token)