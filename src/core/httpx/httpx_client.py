from .base import BaseHttpxClient

from core.config import settings


httpx_client = BaseHttpxClient(
    max_concurrency=settings.httpx.max_concurrency,
    max_connections=settings.httpx.max_connections,
    max_keepalive=settings.httpx.max_keepalive,
    timeout_connect=settings.httpx.timeout_connect,
    timeout_read=settings.httpx.timeout_read,
    timeout_write=settings.httpx.timeout_write,
    timeout_pool=settings.httpx.timeout_pool,
)