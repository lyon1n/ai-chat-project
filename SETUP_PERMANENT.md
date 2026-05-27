# 永久部署（只需 1 个密钥）

前端已固定地址：**https://lyon1n.github.io/ai-chat-project/**

后端使用 **Render 免费托管** + **SQLite**（无需单独购买 MySQL）。

## 你只需要做 1 件事

### 获取 Render API Key

1. 打开 https://dashboard.render.com/u/settings#api-keys
2. 登录 / 注册 Render（可用 GitHub 登录）
3. 点击 **Create API Key**，复制密钥（形如 `rnd_...`）

### 在终端执行（把密钥粘贴进去）

```powershell
cd c:\Users\acer\Desktop\ai-chat-project
gh secret set RENDER_API_KEY --repo lyon1n/ai-chat-project
# 提示输入时粘贴 rnd_ 开头的密钥

gh workflow run "Deploy Backend (Render)" --repo lyon1n/ai-chat-project
```

等待约 5–10 分钟，在 Actions 页面看到绿色 ✓ 后：

- 后端：`https://ai-chat-api.onrender.com`（或日志里显示的地址）
- 前端会自动更新并指向该后端

## 已自动配置好的密钥

| Secret | 说明 |
|--------|------|
| `DEEPSEEK_API_KEY` | 已从本地 `.env` 写入 GitHub |
| `JWT_SECRET_KEY` | 已自动生成 |
| `VITE_API_URL` | 后端部署成功后由 Actions 自动更新 |

## 验证

1. 打开 https://lyon1n.github.io/ai-chat-project/
2. 注册 → 登录 → 上传 PDF → 提问

## 说明

- Render 免费版冷启动约 30–60 秒，首次请求会慢
- 数据存在 Render 磁盘（SQLite + Chroma），重启不丢
- 不再需要本机开 `uvicorn` 或 localtunnel
