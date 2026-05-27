from sentence_transformers import SentenceTransformer

# 加载模型
model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

# 获取 embedding
def get_embedding(text):

    embedding = model.encode(text)

    return embedding