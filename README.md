# AI Chat（PDF 知识库问答）

基于 FastAPI + React + DeepSeek + Chroma 的多用户 RAG 聊天系统。

## 本地开发

### 后端

```bash
pip install -r requirements.txt
cp .env.example .env   # 填写 DEEPSEEK_API_KEY 等
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

### 第一步：代码推送到 GitHub

```bash
git init
git add .
git commit -m "deploy: ai chat project"
git remote add origin https://github.com/你的用户名/ai-chat-project.git
git push -u origin main
```

### 第二步：部署后端（Render）

1. 打开 [Render](https://render.com) → **New Web Service**
2. 连接 GitHub 仓库
3. 配置：
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. 添加 **Persistent Disk**（1GB，挂载 `/data`），否则 Chroma 数据重启会丢失
5. 环境变量（参考 `.env.example`）：

| 变量 | 说明 |
|------|------|
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 |
| `JWT_SECRET_KEY` | JWT 签名密钥（随机长字符串） |
| `DATABASE_URL` | 云端 MySQL 连接串 |
| `MYSQL_SSL` | `true`（PlanetScale 必填） |
| `ALLOWED_ORIGINS` | `https://你的项目.vercel.app` |
| `CHROMA_PATH` | `/data/chroma_db` |
| `UPLOAD_DIR` | `/data/uploads` |

6. 部署完成后访问 `https://xxx.onrender.com/health` 应返回 `{"status":"ok"}`

> 也可直接导入仓库根目录的 `render.yaml` 一键配置。

### 第三步：部署数据库

**方案 A：Render MySQL**

- Render Dashboard → New → PostgreSQL/MySQL
- 复制 Internal/External Database URL 到 `DATABASE_URL`

**方案 B：PlanetScale / 其他 MySQL**

- 创建数据库，获取连接 URL
- 填入 Render 的 `DATABASE_URL`
- 设置 `MYSQL_SSL=true`

表会在后端 **startup** 时自动创建（`users`、`chat_messages`）。

### 第四步：部署前端（Vercel）

1. 打开 [Vercel](https://vercel.com) → **Import Project**
2. 选择同一 GitHub 仓库
3. **Root Directory** 设为 `frontend`
4. **Environment Variables**：

```
VITE_API_URL = https://你的项目.onrender.com
```

5. Deploy

### 第五步：联调检查

| 检查项 | 预期 |
|--------|------|
| 前端能打开 | Vercel 地址正常 |
| 注册/登录 | 无 CORS 报错 |
| 上传 PDF | 左侧出现知识库 |
| 聊天 | 流式回复正常 |
| 换账号登录 | 看不到其他用户数据 |

### 自定义域名（可选）

- Vercel：Settings → Domains → 绑定 `www.xxx.com`
- Render：Settings → Custom Domains → 绑定 `api.xxx.com`
- 更新 `ALLOWED_ORIGINS` 和 `VITE_API_URL`

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
