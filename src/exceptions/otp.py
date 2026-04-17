from .base import AppException


class InvalidOtpError(AppException):
    status_code = 400
    code = "INVALID_OTP"
    detail = "Неверный или просроченный код подтверждения"


class OtpTooFrequentError(AppException):
    status_code = 429
    code = "OTP_TOO_FREQUENT"
    detail = "Слишком частые запросы на получение OTP"


class OtpRateLimitExceededError(AppException):
    status_code = 429
    code = "OTP_RATE_LIMIT_EXCEEDED"
    detail = "Превышен лимит запросов на получение OTP"