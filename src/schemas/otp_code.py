from pydantic import (
    BaseModel,
    ConfigDict,
)

from .token import AccessTokenResponse


class OtpCodeRequest(BaseModel):
    otp_code: str


class OtpCodeResponse(BaseModel):
    message: str = "OTP code confirmed successfully"
    token: AccessTokenResponse

    model_config = ConfigDict(
        from_attributes=True,
    )