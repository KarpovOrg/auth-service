from pydantic import (
    BaseModel,
    EmailStr,
    ConfigDict,
    Field,
)

from .token import AccessTokenResponse


class AuthBase(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=32)


class RegisterRequest(AuthBase):
    pass


class LoginRequest(AuthBase):
    pass


class RegisterResponse(BaseModel):
    message: str = "User registered successfully"
    token: AccessTokenResponse

    model_config = ConfigDict(
        from_attributes=True,
    )


class LoginResponse(BaseModel):
    message: str = "User logged in successfully"
    token: AccessTokenResponse

    model_config = ConfigDict(
        from_attributes=True,
    )


