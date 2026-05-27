import os

from auth import create_token, get_user
from chat_db import (
    delete_chat_history,
    display_collection,
    get_chat_history,
    init_chat_messages_table,
    normalize_collection,
    save_chat_message,
    scoped_collection,
)
from chunk import split_text
from chroma_utils import (
    client as chroma_client,
    delete_collection,
    get_collection_count,
    save_chunks,
    search_chunks,
)
from document_store import get_document_info, load_from_disk, set_chunks
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
from pdf_utils import read_pdf
from pydantic import BaseModel
from starlette.responses import StreamingResponse
from user_db import authenticate_user, create_user, get_user_by_username, init_users_table

load_dotenv()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")

openai_client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

app = FastAPI()


@app.on_event("startup")
def on_startup():
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    init_users_table()
    init_chat_messages_table()
    load_from_disk()


def _cors_origins():
    raw = os.getenv("ALLOWED_ORIGINS", "*")
    if raw.strip() == "*":
        return ["*"]
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class ChatRequest(BaseModel):
    message: str
    collection: str | None = None


def get_current_user(authorization: str | None = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="未登录，请先登录")
    token = (
        authorization.replace("Bearer ", "")
        if authorization.startswith("Bearer ")
        else authorization
    )
    try:
        return get_user(token)
    except ValueError:
        raise HTTPException(status_code=401, detail="token 无效或已过期")


def user_chroma_name(user_id: int, collection: str) -> str:
    return scoped_collection(user_id, collection)


def list_user_collections(user_id: int):
    prefix = f"u{user_id}_"
    items = []
    for c in chroma_client.list_collections():
        if c.name.startswith(prefix):
            display_name = display_collection(c.name, user_id)
            items.append({
                "name": display_name,
                "chunk_count": get_collection_count(c.name),
            })
    return items


def build_rag_prompt(question: str, chunks: list[str]) -> str:
    parts = "\n\n---\n\n".join(
        f"【片段 {i + 1}】\n{c}" for i, c in enumerate(chunks)
    )
    return f"""以下「文档片段」来自用户已选择的知识库，请优先依据片段内容回答。

{parts}

用户问题：
{question}

注意：片段中若包含与问题相关的信息，请直接回答，不要说未收到文档。"""


def build_messages_for_api(
    user_question: str, collection: str | None, user_id: int
):
    history = get_chat_history(collection, user_id)
    messages = []

    if collection:
        messages.append({
            "role": "system",
            "content": (
                "用户已选择知识库，你会在每条最新消息中收到相关文档片段。"
                "请根据片段作答，不要声称看不到或未收到用户文档。"
            ),
        })

    chroma_name = user_chroma_name(user_id, collection) if collection else None

    for i, msg in enumerate(history):
        content = msg["content"]
        if chroma_name and msg["role"] == "user" and i == len(history) - 1:
            top_chunks = search_chunks(chroma_name, user_question, top_k=3)
            if top_chunks:
                content = build_rag_prompt(user_question, top_chunks)
        messages.append({"role": msg["role"], "content": content})

    return messages


@app.post("/register")
def register(data: RegisterRequest):
    if not data.username.strip() or not data.password:
        raise HTTPException(status_code=400, detail="用户名和密码不能为空")
    if len(data.password) < 6:
        raise HTTPException(status_code=400, detail="密码至少 6 位")

    if get_user_by_username(data.username):
        raise HTTPException(status_code=400, detail="用户名已存在")

    create_user(data.username.strip(), data.password)
    return {"message": "注册成功"}


@app.post("/login")
def login(data: LoginRequest):
    user = authenticate_user(data.username, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="账号或密码错误")

    token = create_token({
        "user_id": user["id"],
        "username": user["username"],
    })
    return {"token": token, "username": user["username"]}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/history")
def get_history(
    collection: str = "",
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]
    return get_chat_history(collection or None, user_id)


@app.delete("/history")
def clear_history(
    collection: str = "",
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]
    delete_chat_history(collection or None, user_id)
    return {"message": "对话已清空"}


@app.get("/collections")
async def get_collections(current_user: dict = Depends(get_current_user)):
    return {"collections": list_user_collections(current_user["user_id"])}


@app.delete("/collections/{name}")
async def remove_collection(
    name: str,
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]
    chroma_name = user_chroma_name(user_id, name)
    existing = {c.name for c in chroma_client.list_collections()}
    if chroma_name not in existing:
        raise HTTPException(status_code=404, detail=f"知识库「{name}」不存在")
    delete_collection(chroma_name)
    delete_chat_history(name, user_id)
    return {"message": f"已删除知识库「{name}」"}


@app.get("/document/status")
def document_status(current_user: dict = Depends(get_current_user)):
    return get_document_info()


@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="仅支持 PDF 文件")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    content = await file.read()

    with open(file_path, "wb") as f:
        f.write(content)

    pdf_text = read_pdf(file_path)
    if not pdf_text or not pdf_text.strip():
        raise HTTPException(
            status_code=400,
            detail="PDF 未提取到文字，可能是扫描版，请换一份可选中文字的 PDF",
        )

    chunks = [c for c in split_text(pdf_text) if c.strip()]
    if not chunks:
        raise HTTPException(status_code=400, detail="PDF 内容为空，无法建立知识库")

    base_name = file.filename.replace(".pdf", "").replace(".PDF", "")
    user_id = current_user["user_id"]
    chroma_name = user_chroma_name(user_id, base_name)
    save_chunks(chroma_name, chunks)
    set_chunks(chunks, file.filename)

    return {
        "message": "上传并向量化成功",
        "collection": base_name,
        "chunk_count": len(chunks),
    }


@app.post("/chat")
def chat(
    data: ChatRequest,
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]

    if data.collection:
        chroma_name = user_chroma_name(user_id, data.collection)
        existing = {c.name for c in chroma_client.list_collections()}
        if chroma_name not in existing:
            raise HTTPException(
                status_code=400,
                detail=f"知识库「{data.collection}」不存在，请重新选择",
            )

    collection_key = normalize_collection(data.collection)

    save_chat_message("user", data.message, collection_key, user_id)

    messages = build_messages_for_api(data.message, data.collection, user_id)

    response = openai_client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        stream=True,
    )

    def generate():
        full_reply = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_reply += content
                yield content
        save_chat_message("assistant", full_reply, collection_key, user_id)

    return StreamingResponse(generate(), media_type="text/plain")


STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
