import uvicorn

from fastapi import FastAPI

from api import api_router

from core.config import settings

from core.handlers import app_exception_handler

from core.lifespan import lifespan

from exceptions import AppException


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app.app_name,
        lifespan=lifespan
    )
    app.include_router(api_router, prefix=settings.api.prefix)
    app.add_exception_handler(
        AppException,
        app_exception_handler,
    )
    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.app.host,
        port=settings.app.port,
    )