from datetime import (
    datetime,
    timedelta,
    timezone,
)

from uuid import UUID

from schemas import (
    RegisterRequest,
    UserCreate,
    RefreshTokenCreate,
    SessionCreate,
    AccessRefreshTokens,
    OtpCodeRequest,
    LoginRequest,
)

from exceptions import (
    EmailAlreadyExistsError,
    OtpTooFrequentError,
    OtpRateLimitExceededError,
    InvalidOtpError,
    AuthenticationRequiredError,
    InvalidCredentialsError,
    UserInactiveError,
    InvalidRefreshTokenError,
)

from core.config import settings

from core.database import UnitOfWork

from core.logging import logger

from core.redis import redis_client

from core.security.generators import generate_otp_code
from core.security import (
    get_user_agent,
    hash_password, verify_password,
)
from core.security.token import (
    create_access_token,
    create_refresh_token,
    TokenSubject, hash_refresh_token,
)

from tasks import send_email_confirmation


class AuthService:
    def __init__(
            self,
            uow: UnitOfWork,
    ) -> None:
        self.uow = uow

    async def _create_user(self, schema: UserCreate):
        user = await self.uow.user_repository.upsert_user(schema=schema)
        return user

    @staticmethod
    async def _check_otp_code_rate_limit(user_id: int):
        now_ts = int(datetime.now(timezone.utc).timestamp())
        key = f"otp:{user_id}:timestamps"

        timestamps = await redis_client.lrange(key=key, start=0, end=-1)
        timestamps = list(map(int, timestamps))

        if timestamps and now_ts - timestamps[-1] < settings.otp.resend_interval:
            raise OtpTooFrequentError()

        window_start = now_ts - settings.otp.window_seconds
        timestamps = [t for t in timestamps if t >= window_start]

        if len(timestamps) >= settings.otp.max_per_window:
            raise OtpRateLimitExceededError()

        timestamps.append(now_ts)
        await redis_client.delete(key=key)
        if timestamps:
            await redis_client.rpush(key, *timestamps)
            await redis_client.expire(key=key, seconds=settings.otp.window_seconds)

    @staticmethod
    async def _get_user_agent(header: str) -> str:
        return get_user_agent(user_agent=header)

    async def _create_session(
            self,
            user_id: int,
            header: str,
    ):
        device_type = await self._get_user_agent(header=header)
        session = await self.uow.session_repository.create(
            schema=SessionCreate(
                device_type=device_type,
                user_id=user_id,
            ),
        )
        return session

    async def _create_tokens(
            self,
            user_id: int,
            session_id: int,
            session_uid: str,
            is_verified: bool,
    ):
        access_token = create_access_token(
            subject=TokenSubject(
                user_id=user_id,
                session_uid=session_uid,
                is_verified=is_verified,
            ),
        )

        plain_token, hash_token = create_refresh_token()

        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.jwt.refresh_token_expires,
        )

        await self.uow.refresh_token_repository.create(
            schema=RefreshTokenCreate(
                user_id=user_id,
                session_id=session_id,
                token_hash=hash_token,
                expires_at=expires_at,
            ),
        )

        return AccessRefreshTokens(
            access_token=access_token,
            refresh_token=plain_token,
        )

    async def registration(
            self,
            schema: RegisterRequest,
            header: str,
    ) -> AccessRefreshTokens:
        logger.info(f"Регистрация пользователя '{schema.email}'")

        password = hash_password(password=schema.password)

        user = await self._create_user(
            schema=UserCreate(
                email=schema.email,
                password_hash=password,
            ),
        )

        if user.is_verified:
            logger.warning(
                f"Пользователь '{schema.email}' уже существует"
            )
            raise EmailAlreadyExistsError(email=schema.email)

        await self._check_otp_code_rate_limit(user_id=user.id)

        otp_key = f"otp:{user.id}:code"
        otp_code = await redis_client.get(key=otp_key)

        if not otp_code:
            otp_code = generate_otp_code()
            await redis_client.set(
                key=otp_key,
                value=otp_code,
                ttl=settings.otp.ttl_seconds,
            )

        session = await self._create_session(
            user_id=user.id,
            header=header,
        )

        tokens = await self._create_tokens(
            user_id=user.id,
            session_id=session.id,
            session_uid=str(session.uid),
            is_verified=user.is_verified,
        )

        await self.uow.commit()

        try:
            await send_email_confirmation.async_task(
                email_to=user.email,
                otp_code=otp_code,
            )
        except Exception as e:
            logger.error(
                f"Ошибка при отправке кода подтверждения на почту '{user.email}': {e}"
            )

        return tokens

    async def confirm_registration(
            self,
            user_id: int,
            session_uid: str,
            schema: OtpCodeRequest,
    ):
        otp_key = f"otp:{user_id}:code"
        stored_otp_code = await redis_client.get(key=otp_key)

        if not stored_otp_code or stored_otp_code != schema.otp_code:
            logger.warning(f"Неверный код подтверждения для пользователя с id {user_id}")
            raise InvalidOtpError()

        user = await self.uow.user_repository.set_verified(user_id=user_id)
        if not user:
            logger.error(f"Пользователь с id {user_id} не найден при подтверждении регистрации")
            return AuthenticationRequiredError()

        session = await self.uow.session_repository.get_by_uid(obj_uid=UUID(session_uid))
        if not session:
            raise AuthenticationRequiredError()

        tokens = await self._create_tokens(
            user_id=user.id,
            session_id=session.id,
            session_uid=str(session.uid),
            is_verified=user.is_verified,
        )

        await redis_client.delete(key=otp_key)

        await self.uow.commit()

        return tokens

    async def login(
            self,
            schema: LoginRequest,
            header: str,
    ) -> AccessRefreshTokens:
        logger.info(f"Попытка входа пользователя '{schema.email}'")

        user = await self.uow.user_repository.get_by_email(email=str(schema.email))

        if not user or not verify_password(
                plain_password=schema.password,
                hashed_password=user.password_hash,
        ):
            raise InvalidCredentialsError()

        if not user.is_active:
            raise UserInactiveError()

        session = await self._create_session(user_id=user.id, header=header)

        tokens = await self._create_tokens(
            user_id=user.id,
            session_id=session.id,
            session_uid=str(session.uid),
            is_verified=user.is_verified,
        )

        await self.uow.commit()

        logger.info(f"Пользователь '{schema.email}' успешно вошёл в систему")
        return tokens

    async def logout(
            self,
            plain_refresh_token: str,
    ) -> None:
        token_hash = hash_refresh_token(plain_refresh_token)

        refresh_token = await self.uow.refresh_token_repository.get_valid_by_hash(
            token_hash=token_hash,
        )
        if not refresh_token:
            raise InvalidRefreshTokenError()

        await self.uow.refresh_token_repository.revoke(token_id=refresh_token.id)
        await self.uow.session_repository.deactivate(session_id=refresh_token.session_id)

        await self.uow.commit()

        logger.info(
            f"Пользователь с id {refresh_token.user_id} вышел из системы, "
            f"сессия {refresh_token.session_id} деактивирована"
        )

    async def refresh_tokens(
            self,
            plain_refresh_token: str,
    ) -> AccessRefreshTokens:
        token_hash = hash_refresh_token(plain_refresh_token)

        refresh_token = await self.uow.refresh_token_repository.get_valid_by_hash(
            token_hash=token_hash,
        )
        if not refresh_token:
            raise InvalidRefreshTokenError()

        # Проверяем, что сессия ещё активна
        session = await self.uow.session_repository.get_by_id(
            obj_id=refresh_token.session_id,
        )
        if not session or not session.is_active:
            raise InvalidRefreshTokenError()

        user = await self.uow.user_repository.get_by_id(obj_id=refresh_token.user_id)
        if not user:
            raise InvalidRefreshTokenError()

        if not user.is_active:
            raise UserInactiveError()

        # Ротация: отзываем старый токен и выдаём новую пару
        await self.uow.refresh_token_repository.revoke(token_id=refresh_token.id)

        tokens = await self._create_tokens(
            user_id=user.id,
            session_id=session.id,
            session_uid=str(session.uid),
            is_verified=user.is_verified,
        )

        await self.uow.commit()

        logger.info(f"Токены обновлены для пользователя с id {user.id}")
        return tokens