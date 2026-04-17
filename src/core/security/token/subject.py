from typing import TypedDict


class TokenSubject(TypedDict):
    user_id: int # user id
    session_uid: str # session uid
    is_verified: bool # user is verified
