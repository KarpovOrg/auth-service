from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


BASE_DIR = Path(__file__).parent.parent.parent
ENV_PATH = BASE_DIR / ".env"


class AppConfig(BaseModel):
    app_name: str
    debug: bool


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"
    auth: str = "/auth"


class ApiPrefix(BaseModel):
    prefix: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()


class DatabaseConfig(BaseModel):
    url: str


class RedisConfig(BaseModel):
    url: str
    max_connections: int


class JWTConfig(BaseModel):
    secret_key: str
    algorithm: str
    access_token_expires: int
    refresh_token_expires: int
    access_token_cookie_key: str
    refresh_token_cookie_key: str


class OTPConfig(BaseModel):
    resend_interval: int
    max_per_window: int
    window_seconds: int
    ttl_seconds: int


class HttpxConfig(BaseModel):
    max_concurrency: int
    max_connections: int
    max_keepalive: int
    timeout_connect: float
    timeout_read: float
    timeout_write: float
    timeout_pool: float


class ResendConfig(BaseModel):
    api_key: str
    from_email: str


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="AUTH_CONFIG__",
    )
    app: AppConfig
    api: ApiPrefix = ApiPrefix()
    db: DatabaseConfig
    redis: RedisConfig
    jwt: JWTConfig
    otp: OTPConfig
    httpx: HttpxConfig
    resend: ResendConfig


settings = Settings()