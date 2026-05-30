from fastapi import APIRouter, Depends, HTTPException
from openai import OpenAI
from starlette.responses import StreamingResponse

from .chat_db import (
    delete_chat_history,
    get_chat_history,
    normalize_collection,
    save_chat_message,
)
from .chat_service import build_messages_for_api
from .collection_service import ensure_collection_exists
from .config import deepseek_api_key, llm_timeout_seconds
from .dependencies import get_current_user
from .schemas import ChatRequest

router = APIRouter()

openai_client = OpenAI(
    api_key=deepseek_api_key() or "missing-local-key",
    base_url="https://api.deepseek.com",
    timeout=llm_timeout_seconds(),
)


@router.get("/history")
def get_history(
    collection: str = "",
    current_user: dict = Depends(get_current_user),
):
    return get_chat_history(collection or None, current_user["user_id"])


@router.delete("/history")
def clear_history(
    collection: str = "",
    current_user: dict = Depends(get_current_user),
):
    delete_chat_history(collection or None, current_user["user_id"])
    return {"message": "对话已清空"}


@router.post("/chat")
def chat(data: ChatRequest, current_user: dict = Depends(get_current_user)):
    message = data.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="消息不能为空")

    user_id = current_user["user_id"]
    if data.collection:
        ensure_collection_exists(user_id, data.collection)

    collection_key = normalize_collection(data.collection)
    save_chat_message("user", message, collection_key, user_id)
    messages = build_messages_for_api(message, data.collection, user_id)

    try:
        response = openai_client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            stream=True,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="模型服务暂时不可用，请稍后重试",
        ) from exc

    def generate():
        full_reply = ""
        try:
            for chunk in response:
                content = chunk.choices[0].delta.content
                if content:
                    full_reply += content
                    yield content
        except Exception:
            fallback = "\n\n[模型响应中断，请稍后重试]"
            full_reply += fallback
            yield fallback
        finally:
            if full_reply:
                save_chat_message("assistant", full_reply, collection_key, user_id)

    return StreamingResponse(generate(), media_type="text/plain; charset=utf-8")
