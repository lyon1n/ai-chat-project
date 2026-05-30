from fastapi import Header, HTTPException

from .auth import get_user


def get_current_user(authorization: str | None = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="未登录，请先登录")

    scheme, _, value = authorization.partition(" ")
    token = value if scheme.lower() == "bearer" and value else authorization

    try:
        return get_user(token)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="token 无效或已过期") from exc
