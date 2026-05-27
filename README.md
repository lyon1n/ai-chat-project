# AI Chat（PDF 知识库问答）

基于 FastAPI + React + DeepSeek + Chroma 的多用户 RAG 聊天系统。

## 项目结构

```
ai-chat-project/
├── backend/              # 后端（FastAPI）
│   ├── main.py           # API 入口
│   ├── auth.py           # JWT 认证
│   ├── db.py             # 数据库连接（SQLite / MySQL）
│   ├── chat_db.py        # 聊天记录
│   ├── user_db.py        # 用户表
│   ├── chroma_utils.py   # Chroma 向量库
│   ├── pdf_utils.py      # PDF 解析
│   ├── chunk.py          # 文本分块
│   └── document_store.py # 文档缓存
├── frontend/             # 前端（React + Vite）
│   └── src/
├── scripts/
│   └── start-local.ps1   # 本地启动脚本
├── start-local.bat       # 双击启动
├── requirements.txt
└── .env.example
```

## 本地运行

### 一键启动

1. 复制 `.env.example` 为 `.env`，填写 `DEEPSEEK_API_KEY`
2. 双击 **`start-local.bat`**
3. 浏览器打开 **http://127.0.0.1:5173**

### 手动启动

**终端 1 - 后端：**
```bash
python -m venv venv
venv\Scripts\pip install -r requirements.txt
set USE_SQLITE=true
venv\Scripts\uvicorn backend.main:app --reload
```

**终端 2 - 前端：**
```bash
cd frontend
npm install
npm run dev
```

## 功能

- 注册 / 登录（JWT，多用户隔离）
- 上传 PDF 创建知识库
- RAG 文档问答（Chroma 向量检索 + DeepSeek）
- 多知识库切换、删除

## 技术栈

| 层 | 技术 |
|----|------|
| 后端 | FastAPI、ChromaDB、PyPDF |
| 前端 | React、Vite |
| AI | DeepSeek API |
| 数据库 | SQLite（本地）/ MySQL（可选） |
