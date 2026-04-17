from pydantic import (
    BaseModel,
    ConfigDict,
)


class TokenBase(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AccessRefreshTokens(TokenBase):
    refresh_token: str
    model_config = ConfigDict(
        from_attributes=True,
    )


class AccessTokenResponse(TokenBase):
    model_config = ConfigDict(
        from_attributes=True,
    )