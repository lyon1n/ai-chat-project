from backend.chroma_utils import delete_collection, save_chunks
from backend.collection_service import list_user_collections, user_chroma_name


def test_non_ascii_collection_names_are_not_collapsed():
    assert user_chroma_name(1, "合同") != user_chroma_name(1, "说明书")


def test_collections_are_scoped_by_user():
    name_a = user_chroma_name(101, "shared")
    name_b = user_chroma_name(202, "shared")

    try:
        save_chunks(name_a, [{"content": "用户 A 文档", "metadata": {"source": "a.pdf"}}], "shared")
        save_chunks(name_b, [{"content": "用户 B 文档", "metadata": {"source": "b.pdf"}}], "shared")

        user_a_collections = list_user_collections(101)
        user_b_collections = list_user_collections(202)

        assert user_a_collections == [{"name": "shared", "chunk_count": 1}]
        assert user_b_collections == [{"name": "shared", "chunk_count": 1}]
    finally:
        delete_collection(name_a)
        delete_collection(name_b)
