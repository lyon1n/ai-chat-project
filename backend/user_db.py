from .db import get_connection, is_sqlite, sql
from .auth import hash_password, verify_password


def init_users_table():
    conn = get_connection()
    cursor = conn.cursor()
    if is_sqlite():
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
            """
        )
    else:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                password VARCHAR(200) NOT NULL
            )
            """
        )
    conn.commit()
    cursor.close()
    conn.close()


def create_user(username: str, password: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    hashed = hash_password(password)
    cursor.execute(
        sql(
            """
            INSERT INTO users (username, password)
            VALUES (%s, %s)
            """
        ),
        (username, hashed),
    )
    conn.commit()
    user_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return user_id


def get_user_by_username(username: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        sql("SELECT id, username, password FROM users WHERE username = %s"),
        (username,),
    )
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if is_sqlite() and user is not None:
        return {
            "id": user["id"],
            "username": user["username"],
            "password": user["password"],
        }
    return user


def authenticate_user(username: str, password: str):
    user = get_user_by_username(username)
    if not user:
        return None
    if not verify_password(password, user["password"]):
        return None
    return {"id": user["id"], "username": user["username"]}
