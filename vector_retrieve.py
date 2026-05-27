from embedding_utils import get_embedding
from similarity import cosine_similarity

def retrieve_by_embedding(question, chunks):
    if not chunks:
        raise ValueError("没有可用的文档文本块，请先上传 PDF")

    # 问题 embedding
    question_embedding = get_embedding(question)

    scores = []

    # 和每个 chunk 比较
    for chunk in chunks:

        chunk_embedding = get_embedding(chunk)

        score = cosine_similarity(
            question_embedding,
            chunk_embedding
        )

        scores.append((chunk, score))

    # 按相似度排序
    scores.sort(
        key=lambda x: x[1],
        reverse=True
    )

    return scores


def retrieve_top_chunks(question, chunks, top_k=3):
    scores = retrieve_by_embedding(question, chunks)
    return [chunk for chunk, _ in scores[:top_k]]