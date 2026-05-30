from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .chat_db import init_chat_messages_table
from .config import allowed_origins
from .paths import upload_dir
from .routes_auth import router as auth_router
from .routes_chat import router as chat_router
from .routes_collections import router as collections_router
from .routes_upload import router as upload_router
from .user_db import init_users_table


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(upload_dir(), exist_ok=True)
    init_users_table()
    init_chat_messages_table()
    yield


app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(collections_router)
app.include_router(upload_router)


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("backend.main:app", host="127.0.0.1", port=port, reload=True)
