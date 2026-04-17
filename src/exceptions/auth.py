from .base import AppException


class EmailAlreadyExistsError(AppException):
    status_code = 409
    code = "EMAIL_ALREADY_EXISTS"

    def __init__(self, email: str) -> None:
        super().__init__(f"Электронная почта '{email}' уже используется")


class AuthenticationRequiredError(AppException):
    status_code = 401
    code = "AUTH_REQUIRED"
    detail = "Требуется аутентификация"


class InvalidCredentialsError(AppException):
    status_code = 403
    code = "INVALID_CREDENTIALS"
    detail = "Неверный логин или пароль"


class InvalidRefreshTokenError(AppException):
    status_code = 401
    code = "INVALID_REFRESH_TOKEN"
    detail = "Refresh токен недействителен, отозван или истёк"


class UserInactiveError(AppException):
    status_code = 403
    code = "USER_INACTIVE"
    detail = "Аккаунт пользователя заблокирован"
