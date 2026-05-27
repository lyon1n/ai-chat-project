import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def project_path(*parts: str) -> str:
    return os.path.join(ROOT_DIR, *parts)


def upload_dir() -> str:
    return os.getenv("UPLOAD_DIR", project_path("uploads"))


def chroma_dir() -> str:
    return os.getenv("CHROMA_PATH", project_path("chroma_db"))


def sqlite_path() -> str:
    return os.getenv("SQLITE_PATH", project_path("chat.db"))
