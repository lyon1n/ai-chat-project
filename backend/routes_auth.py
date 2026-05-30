from fastapi import APIRouter, HTTPException

from .auth import create_token
from .schemas import LoginRequest, RegisterRequest
from .user_db import authenticate_user, create_user, get_user_by_username

router = APIRouter()


@router.post("/register")
def register(data: RegisterRequest):
    username = data.username.strip()
    if not username or not data.password:
        raise HTTPException(status_code=400, detail="用户名和密码不能为空")
    if len(username) > 50:
        raise HTTPException(status_code=400, detail="用户名不能超过 50 个字符")
    if len(data.password) < 6:
        raise HTTPException(status_code=400, detail="密码至少 6 位")

    if get_user_by_username(username):
        raise HTTPException(status_code=400, detail="用户名已存在")

    create_user(username, data.password)
    return {"message": "注册成功"}


@router.post("/login")
def login(data: LoginRequest):
    user = authenticate_user(data.username.strip(), data.password)
    if not user:
        raise HTTPException(status_code=401, detail="账号或密码错误")

    token = create_token(
        {
            "user_id": user["id"],
            "username": user["username"],
        }
    )
    return {"token": token, "username": user["username"]}
