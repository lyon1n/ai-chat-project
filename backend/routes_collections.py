from fastapi import APIRouter, Depends, HTTPException

from .chat_db import delete_chat_history
from .chroma_utils import delete_collection
from .collection_service import (
    collection_exists,
    list_user_collections,
    user_chroma_name,
    user_document_status,
)
from .dependencies import get_current_user
from .upload_utils import remove_uploads_for_collection

router = APIRouter()


@router.get("/collections")
async def get_collections(current_user: dict = Depends(get_current_user)):
    return {"collections": list_user_collections(current_user["user_id"])}


@router.delete("/collections/{name}")
async def remove_collection(name: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    if not collection_exists(user_id, name):
        raise HTTPException(status_code=404, detail=f"知识库「{name}」不存在")

    delete_collection(user_chroma_name(user_id, name))
    delete_chat_history(name, user_id)
    remove_uploads_for_collection(user_id, name)
    return {"message": f"已删除知识库「{name}」"}


@router.get("/document/status")
def document_status(current_user: dict = Depends(get_current_user)):
    return user_document_status(current_user["user_id"])
