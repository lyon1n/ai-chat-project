import os

from dotenv import load_dotenv

from .paths import ROOT_DIR

load_dotenv(os.path.join(ROOT_DIR, ".env"))


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def is_production() -> bool:
    return os.getenv("APP_ENV", "").lower() in {"prod", "production"}


def jwt_secret_key() -> str:
    secret = os.getenv("JWT_SECRET_KEY")
    if secret:
        return secret
    if is_production():
        raise RuntimeError("JWT_SECRET_KEY must be set in production")
    return "ai-chat-local-dev-secret"


def allowed_origins() -> list[str]:
    raw = os.getenv("ALLOWED_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173")
    if raw.strip() == "*":
        return ["*"]
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


def max_upload_bytes() -> int:
    return _env_int("MAX_UPLOAD_MB", 20) * 1024 * 1024


def chat_history_limit() -> int:
    return _env_int("CHAT_HISTORY_LIMIT", 20)


def llm_timeout_seconds() -> float:
    return _env_float("LLM_TIMEOUT_SECONDS", 60.0)


def deepseek_api_key() -> str | None:
    return os.getenv("DEEPSEEK_API_KEY")
