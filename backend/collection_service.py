from fastapi import HTTPException

from .chroma_utils import (
    chroma_storage_name,
    client as chroma_client,
    collection_display_name,
)


def user_chroma_name(user_id: int, collection: str) -> str:
    return chroma_storage_name(user_id, collection)


def list_user_collections(user_id: int):
    prefix = f"u{user_id}_"
    items = []
    for collection in chroma_client.list_collections():
        if collection.name.startswith(prefix):
            items.append(
                {
                    "name": collection_display_name(collection),
                    "chunk_count": collection.count(),
                }
            )
    return sorted(items, key=lambda item: item["name"].lower())


def collection_exists(user_id: int, collection: str) -> bool:
    chroma_name = user_chroma_name(user_id, collection)
    return chroma_name in {item.name for item in chroma_client.list_collections()}


def ensure_collection_exists(user_id: int, collection: str) -> str:
    chroma_name = user_chroma_name(user_id, collection)
    if chroma_name not in {item.name for item in chroma_client.list_collections()}:
        raise HTTPException(
            status_code=400,
            detail=f"知识库「{collection}」不存在，请重新选择",
        )
    return chroma_name


def user_document_status(user_id: int):
    collections = list_user_collections(user_id)
    return {
        "loaded": bool(collections),
        "filename": None,
        "chunk_count": sum(item["chunk_count"] for item in collections),
        "collections": collections,
    }
