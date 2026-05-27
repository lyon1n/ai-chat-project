# AI Chat · PDF 知识库问答

本地运行的多用户 RAG 聊天应用：上传 PDF 建知识库，基于文档向 DeepSeek 提问。

## 功能

- 用户注册 / 登录（JWT，数据按用户隔离）
- 上传 PDF 自动分块、向量化（ChromaDB）
- 选择知识库进行 RAG 问答（流式回复）
- 多知识库管理（切换、删除）

## 技术栈

| 模块 | 技术 |
|------|------|
| 后端 | FastAPI、ChromaDB、PyPDF |
| 前端 | React、Vite |
| 大模型 | DeepSeek API |
| 数据库 | SQLite（默认）/ MySQL（可选） |

## 项目结构

```
ai-chat-project/
├── backend/          # FastAPI 后端
├── frontend/         # React 前端
├── requirements.txt
└── .env.example
```

## 环境要求

- Python 3.10+
- Node.js 18+
- [DeepSeek API Key](https://platform.deepseek.com/)

## 快速开始

### 1. 克隆并配置环境变量

```bash
git clone https://github.com/lyon1n/ai-chat-project.git
cd ai-chat-project
copy .env.example .env        # Windows
# cp .env.example .env        # macOS / Linux
```

编辑 `.env`，至少填写：

```env
DEEPSEEK_API_KEY=你的密钥
USE_SQLITE=true
```

### 2. 安装依赖

```bash
python -m venv venv
venv\Scripts\pip install -r requirements.txt   # Windows
# source venv/bin/activate && pip install -r requirements.txt

cd frontend
npm install
cd ..
```

### 3. 启动（需要两个终端）

**终端 1 · 后端（项目根目录）：**

```bash
set USE_SQLITE=true
venv\Scripts\uvicorn backend.main:app --reload
```

**终端 2 · 前端：**

```bash
cd frontend
npm run dev
```

### 4. 打开浏览器

访问 **http://127.0.0.1:5173**

> **注意：** `8000` 端口是后端 API，不是网页。请访问 `5173` 端口的前端地址。

## 常见问题

**打不开网页？**

- 确认两个终端都在运行（后端 + 前端）
- 访问 `http://127.0.0.1:5173` 或 `http://localhost:5173`
- 不要直接打开 `http://127.0.0.1:8000`

**上传 PDF 失败？**

- 确认 `.env` 中已配置 `DEEPSEEK_API_KEY`
- 使用可选中文字的 PDF（扫描版图片 PDF 无法提取文字）

**登录 / 注册无响应？**

- 确认后端终端无报错，访问 http://127.0.0.1:8000/health 应返回 `{"status":"ok"}`

## 可选：MySQL

默认使用 SQLite（`chat.db`），无需额外安装数据库。若需 MySQL，在 `.env` 中设置：

```env
USE_SQLITE=false
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=你的密码
MYSQL_DATABASE=ai_chat
```
