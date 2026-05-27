# AI Chat（PDF 知识库问答）

基于 FastAPI + React + DeepSeek + Chroma 的多用户 RAG 聊天系统。

## 本地开发

### 后端

```bash
pip install -r requirements.txt
cp .env.example .env   
python init_chat_db.py
uvicorn main:app --reload
```

### 前端

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## 云端部署（Vercel + Render + MySQL）

### 架构

```
用户浏览器
    ↓
Vercel（React 前端）  →  https://xxx.vercel.app
    ↓ API 请求
Render（FastAPI 后端） →  https://xxx.onrender.com
    ↓
云端 MySQL（PlanetScale / Render MySQL）
Chroma 向量库（Render 持久化磁盘 /data）
```

## 项目结构

```
main.py              # FastAPI 入口
auth.py              # JWT 认证
db.py / chat_db.py   # MySQL 操作
chroma_utils.py      # Chroma 向量库
user_db.py           # 用户表
frontend/            # React 前端
render.yaml          # Render 部署配置
.env.example         # 环境变量模板
```
