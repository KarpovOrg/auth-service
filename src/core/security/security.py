from datetime import timedelta

from fastapi_jwt import JwtAccessBearerCookie

from core.config import settings


access_security = JwtAccessBearerCookie(
    secret_key=settings.jwt.secret_key,
    auto_error=False,
    algorithm=settings.jwt.algorithm,
    access_expires_delta=timedelta(minutes=settings.jwt.access_token_expires),
)
