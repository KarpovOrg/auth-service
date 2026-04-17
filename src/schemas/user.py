from pydantic import (
    BaseModel,
    EmailStr,
)


class UserCreate(BaseModel):
    email: EmailStr
    password_hash: str
    name: str | None = None
    surname: str | None = None
    is_verified: bool = False