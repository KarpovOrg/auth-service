from fastapi.responses import JSONResponse
from fastapi import Request

from exceptions import AppException


async def app_exception_handler(
        request: Request,
        exc: AppException,
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "code": exc.code,
        },
    )