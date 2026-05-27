import json
import os

from .paths import upload_dir

UPLOAD_DIR = upload_dir()
CACHE_PATH = os.path.join(UPLOAD_DIR, "document_cache.json")

_chunks = []
_filename = None


def _save_to_disk():
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(
            {"filename": _filename, "chunks": _chunks},
            f,
            ensure_ascii=False,
        )


def load_from_disk():
    global _chunks, _filename
    if not os.path.exists(CACHE_PATH):
        return
    try:
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        _chunks = data.get("chunks") or []
        _filename = data.get("filename")
    except (json.JSONDecodeError, OSError):
        _chunks = []
        _filename = None


def set_chunks(chunks, filename=None):
    global _chunks, _filename
    _chunks = [c for c in chunks if c and c.strip()]
    _filename = filename
    _save_to_disk()


def clear_document():
    global _chunks, _filename
    _chunks = []
    _filename = None
    if os.path.exists(CACHE_PATH):
        os.remove(CACHE_PATH)


def get_chunks():
    return _chunks


def has_document():
    return len(_chunks) > 0


def get_document_info():
    return {
        "loaded": has_document(),
        "filename": _filename,
        "chunk_count": len(_chunks),
    }
