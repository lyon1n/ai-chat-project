import os
from urllib.parse import unquote, urlparse

import pymysql
from dotenv import load_dotenv

load_dotenv()


def _connection_kwargs():
    database_url = os.getenv("DATABASE_URL")
    if database_url:
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


def get_connection():
    return pymysql.connect(**_connection_kwargs())
