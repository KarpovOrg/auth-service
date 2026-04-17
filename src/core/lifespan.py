from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.logging import logger

from core.database import db_client

from core.redis import redis_client

from core.httpx import httpx_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Запуск приложения")
    await redis_client.connect()
    yield
    logger.info("Закрытие соединений с БД...")
    await db_client.dispose()
    logger.info("Закрытие соединений с Redis...")
    await redis_client.disconnect()
    logger.info("Закрытие соединений с HTTPX...")
    await httpx_client.close()
    logger.info("Остановка приложения")