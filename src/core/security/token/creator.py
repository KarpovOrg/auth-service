from uuid import uuid4

from .subject import TokenSubject

from ..security import access_security

from .hasher import hash_refresh_token


def create_access_token(subject: TokenSubject):
    return access_security.create_access_token(
        subject=subject,
    )


def create_refresh_token():
    plain_token = str(uuid4())
    hash_token = hash_refresh_token(plain_token)
    return plain_token, hash_token