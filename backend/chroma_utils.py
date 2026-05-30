import hashlib
import os
import re

import chromadb

from .paths import chroma_dir

CHROMA_PATH = chroma_dir()
os.makedirs(CHROMA_PATH, exist_ok=True)

client = chromadb.PersistentClient(path=CHROMA_PATH)

_CHROMA_NAME_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{1,510}[a-zA-Z0-9]$")


def chroma_storage_name(user_id: int, display_name: str) -> str:
    raw = display_name.strip()
    safe = re.sub(r"[^a-zA-Z0-9._-]", "_", raw)
    safe = re.sub(r"_+", "_", safe).strip("._-")
    if not safe:
        digest = hashlib.md5(raw.encode("utf-8")).hexdigest()[:12]
        return f"u{user_id}_doc_{digest}"
    candidate = f"u{user_id}_{safe}"
    if len(candidate) >= 3 and _CHROMA_NAME_RE.match(candidate):
        return candidate[:512].rstrip("._-")
    digest = hashlib.md5(raw.encode("utf-8")).hexdigest()[:12]
    return f"u{user_id}_doc_{digest}"


def get_collection(name, display_name=None):
    if display_name:
        return client.get_or_create_collection(
            name=name,
            metadata={"display_name": display_name},
        )
    return client.get_or_create_collection(name=name)


def delete_collection(name):
    existing = {c.name for c in client.list_collections()}
    if name in existing:
        client.delete_collection(name)


def get_collection_count(name):
    collection = get_collection(name)
    return collection.count()


def collection_display_name(collection) -> str:
    meta = collection.metadata or {}
    return meta.get("display_name") or collection.name


def _chunk_content(chunk) -> str:
    if isinstance(chunk, dict):
        return chunk.get("content", "")
    return str(chunk)


def _chunk_metadata(chunk, index: int) -> dict:
    metadata = {"chunk_index": index}
    if isinstance(chunk, dict):
        metadata.update(chunk.get("metadata") or {})
    return {
        key: value
        for key, value in metadata.items()
        if isinstance(value, (str, int, float, bool))
    }


def save_chunks(collection_name, chunks, display_name=None):
    delete_collection(collection_name)
    collection = get_collection(collection_name, display_name=display_name)

    documents = [_chunk_content(chunk) for chunk in chunks]
    metadatas = [_chunk_metadata(chunk, index) for index, chunk in enumerate(chunks)]
    ids = [f"{collection_name}_{index}" for index in range(len(documents))]

    if documents:
        collection.add(documents=documents, metadatas=metadatas, ids=ids)


def search_chunks(collection_name, question, top_k=3):
    collection = get_collection(collection_name)
    count = collection.count()
    if count == 0:
        return []

    results = collection.query(
        query_texts=[question],
        n_results=min(top_k, count),
        include=["documents", "metadatas", "distances"],
    )
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    return [
        {
            "content": document,
            "metadata": metadatas[index] or {},
            "distance": distances[index] if index < len(distances) else None,
        }
        for index, document in enumerate(documents)
    ]
