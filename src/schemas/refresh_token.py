from datetime import datetime

from pydantic import BaseModel


class RefreshTokenCreate(BaseModel):
    user_id: int
    session_id: int
    token_hash: str
    expires_at: datetime
