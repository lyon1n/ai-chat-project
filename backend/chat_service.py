from .chat_db import get_chat_history
from .collection_service import user_chroma_name
from .config import chat_history_limit
from .chroma_utils import search_chunks


def _format_source(metadata: dict) -> str:
    parts = []
    source = metadata.get("source")
    page = metadata.get("page")
    if source:
        parts.append(str(source))
    if page:
        parts.append(f"第 {page} 页")
    return f"（{'，'.join(parts)}）" if parts else ""


def build_rag_prompt(question: str, chunks: list[dict]) -> str:
    parts = "\n\n---\n\n".join(
        f"【片段 {index + 1}{_format_source(chunk.get('metadata') or {})}】\n"
        f"{chunk.get('content', '')}"
        for index, chunk in enumerate(chunks)
    )
    return f"""以下「文档片段」来自用户已选择的知识库，请优先依据片段内容回答。

{parts}

用户问题：
{question}

注意：片段中若包含与问题相关的信息，请直接回答；无法从片段确认时，请明确说明依据不足。"""


def build_messages_for_api(user_question: str, collection: str | None, user_id: int):
    history = get_chat_history(collection, user_id, limit=chat_history_limit())
    messages = []

    if collection:
        messages.append(
            {
                "role": "system",
                "content": (
                    "用户已选择知识库，你会在最新用户消息中收到相关文档片段。"
                    "请根据片段作答，并在片段不足时说明依据不足。"
                ),
            }
        )

    rag_content = None
    if collection:
        chroma_name = user_chroma_name(user_id, collection)
        top_chunks = search_chunks(chroma_name, user_question, top_k=4)
        if top_chunks:
            rag_content = build_rag_prompt(user_question, top_chunks)

    for index, msg in enumerate(history):
        content = msg["content"]
        if rag_content and msg["role"] == "user" and index == len(history) - 1:
            content = rag_content
        messages.append({"role": msg["role"], "content": content})

    return messages
