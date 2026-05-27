import os

import chromadb

CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_db")
os.makedirs(CHROMA_PATH, exist_ok=True)

client = chromadb.PersistentClient(path=CHROMA_PATH)


def get_collection(name):
    return client.get_or_create_collection(name=name)


def delete_collection(name):
    try:
        client.delete_collection(name)
    except ValueError:
        pass


def get_collection_count(name):
    collection = get_collection(name)
    return collection.count()


def save_chunks(collection_name, chunks):
    delete_collection(collection_name)
    collection = get_collection(collection_name)

    for index, chunk in enumerate(chunks):
        collection.add(
            documents=[chunk],
            ids=[f"{collection_name}_{index}"],
        )


def search_chunks(collection_name, question, top_k=3):
    collection = get_collection(collection_name)
    count = collection.count()
    if count == 0:
        return []

    results = collection.query(
        query_texts=[question],
        n_results=min(top_k, count),
    )
    return results["documents"][0]
