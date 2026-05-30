import os

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from .chunk import split_pages
from .chroma_utils import save_chunks
from .collection_service import user_chroma_name
from .dependencies import get_current_user
from .pdf_utils import read_pdf_pages
from .upload_utils import save_upload_file

router = APIRouter()


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]
    file_path, safe_filename, collection_name = await save_upload_file(file, user_id)

    try:
        pages = read_pdf_pages(file_path)
    except Exception as exc:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=400, detail="PDF 文件损坏或无法读取") from exc

    if not pages:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=400,
            detail="PDF 未提取到文字，可能是扫描版，请换一份可选中文字的 PDF",
        )

    chunks = split_pages(pages, source=safe_filename)
    if not chunks:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=400, detail="PDF 内容为空，无法建立知识库")

    chroma_name = user_chroma_name(user_id, collection_name)
    try:
        save_chunks(chroma_name, chunks, display_name=collection_name)
    except Exception as exc:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"向量库存储失败：{exc}") from exc

    return {
        "message": "上传并向量化成功",
        "collection": collection_name,
        "chunk_count": len(chunks),
    }
