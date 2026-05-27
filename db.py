import os
import sqlite3
from urllib.parse import unquote, urlparse

import pymysql
from dotenv import load_dotenv

load_dotenv()


def is_sqlite() -> bool:
    database_url = os.getenv("DATABASE_URL", "")
    return (
        os.getenv("USE_SQLITE", "").lower() in {"1", "true", "yes"}
        or database_url.startswith("sqlite:")
    )


def sql(query: str) -> str:
    return query.replace("%s", "?") if is_sqlite() else query


def get_connection():
    if is_sqlite():
        path = os.getenv("SQLITE_PATH", "./chat.db")
        if path != ":memory:":
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        conn = sqlite3.connect(path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    return pymysql.connect(**_mysql_kwargs())


def _mysql_kwargs():
    database_url = os.getenv("DATABASE_URL")
    if database_url and not database_url.startswith("sqlite:"):
        parsed = urlparse(database_url)
        kwargs = {
            "host": parsed.hostname,
            "port": parsed.port or 3306,
            "user": parsed.username,
            "password": unquote(parsed.password or ""),
            "database": parsed.path.lstrip("/").split("?")[0],
            "charset": "utf8mb4",
            "cursorclass": pymysql.cursors.DictCursor,
        }
    else:
        kwargs = {
            "host": os.getenv("MYSQL_HOST", "localhost"),
            "port": int(os.getenv("MYSQL_PORT", "3306")),
            "user": os.getenv("MYSQL_USER", "root"),
            "password": os.getenv("MYSQL_PASSWORD", "123456"),
            "database": os.getenv("MYSQL_DATABASE", "ai_chat"),
            "charset": "utf8mb4",
            "cursorclass": pymysql.cursors.DictCursor,
        }

    if os.getenv("MYSQL_SSL", "").lower() in {"1", "true", "yes"}:
        kwargs["ssl"] = {"ssl": {}}

    return kwargs
