import os
import re
import uuid

from fastapi import HTTPException, UploadFile

from .config import max_upload_bytes
from .paths import upload_dir

_SAFE_NAME_RE = re.compile(r"[^a-zA-Z0-9._\-\u4e00-\u9fff]+")


def sanitize_pdf_filename(filename: str | None) -> tuple[str, str]:
    original = os.path.basename(filename or "")
    stem, ext = os.path.splitext(original)
    if not stem or ext.lower() != ".pdf":
        raise HTTPException(status_code=400, detail="仅支持 PDF 文件")

    safe_stem = _SAFE_NAME_RE.sub("_", stem).strip("._-")[:80] or "document"
    return f"{safe_stem}.pdf", safe_stem


def user_upload_dir(user_id: int) -> str:
    return os.path.join(upload_dir(), f"user_{user_id}")


async def save_upload_file(file: UploadFile, user_id: int) -> tuple[str, str, str]:
    safe_filename, collection_name = sanitize_pdf_filename(file.filename)
    user_dir = user_upload_dir(user_id)
    os.makedirs(user_dir, exist_ok=True)

    stored_filename = f"{uuid.uuid4().hex}_{safe_filename}"
    file_path = os.path.join(user_dir, stored_filename)
    limit = max_upload_bytes()
    total = 0

    try:
        with open(file_path, "wb") as output:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > limit:
                    raise HTTPException(
                        status_code=413,
                        detail=f"PDF 文件不能超过 {limit // 1024 // 1024}MB",
                    )
                output.write(chunk)
    except Exception:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise

    return file_path, safe_filename, collection_name


def remove_uploads_for_collection(user_id: int, collection_name: str) -> None:
    user_dir = user_upload_dir(user_id)
    if not os.path.isdir(user_dir):
        return

    safe_filename, _ = sanitize_pdf_filename(f"{collection_name}.pdf")
    suffix = f"_{safe_filename}"
    for filename in os.listdir(user_dir):
        if filename.endswith(suffix):
            try:
                os.remove(os.path.join(user_dir, filename))
            except OSError:
                pass
