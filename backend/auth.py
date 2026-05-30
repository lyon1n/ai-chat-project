from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from .config import jwt_secret_key

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode(),
        hashed_password.encode(),
    )


def create_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(days=7)
    return jwt.encode(payload, jwt_secret_key(), algorithm=ALGORITHM)


def verify_token(token: str) -> dict:
    return jwt.decode(token, jwt_secret_key(), algorithms=[ALGORITHM])


def get_user(token: str) -> dict:
    try:
        return verify_token(token)
    except JWTError as e:
        raise ValueError("token 无效或已过期") from e
